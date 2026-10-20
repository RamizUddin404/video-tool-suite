from __future__ import annotations

import asyncio
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from huggingface_hub import InferenceClient
from youtube_transcript_api import YouTubeTranscriptApi

from .config import settings
from .schemas import CreateJobRequest

app = FastAPI(
    title="LinkToon Studio API",
    version="0.2.0",
    description="Self-managed LinkToon backend using Hugging Face Inference Providers.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

jobs: dict[str, dict[str, Any]] = {}
VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {
        key: job.get(key)
        for key in ("id", "status", "prompt", "output_url", "error", "created_at", "updated_at", "model")
    }


def extract_youtube_id(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    allowed_hosts = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "youtube-nocookie.com", "www.youtube-nocookie.com"}
    if host not in allowed_hosts:
        raise ValueError("For link mode, provide a YouTube link with public captions, or switch to Topic only and describe the source. Direct video URLs are not video inputs for text-to-video models.")
    video_id = ""
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    else:
        match = re.match(r"^/(?:shorts|embed|live)/([^/?]+)", parsed.path)
        if match:
            video_id = match.group(1)
    if not VIDEO_ID_RE.fullmatch(video_id):
        raise ValueError("Could not identify a valid YouTube video ID from that URL.")
    return video_id


def fetch_caption_context(raw_url: str) -> str:
    video_id = extract_youtube_id(raw_url)
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["bn", "en", "hi"])
    lines: list[str] = []
    total = 0
    for snippet in transcript.snippets:
        text = " ".join(str(snippet.text).split())
        if not text:
            continue
        remaining = 7000 - total
        if remaining <= 0:
            break
        text = text[:remaining]
        lines.append(text)
        total += len(text)
    if not lines:
        raise ValueError("No usable captions were found. Enter a topic or paste the video transcript manually.")
    return " ".join(lines)


def require_client_key(request: Request) -> None:
    expected = settings.app_api_key
    if not expected:
        raise HTTPException(status_code=503, detail="Backend access is locked until APP_API_KEY is configured as a secret on the Space.")
    supplied = request.headers.get("authorization", "")
    if supplied.lower().startswith("bearer "):
        supplied = supplied[7:].strip()
    else:
        supplied = ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid backend access key.")

def generate_video_bytes(prompt: str, model: str) -> bytes:
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not configured on the backend host.")
    client = InferenceClient(
        provider=settings.hf_provider,
        api_key=settings.hf_token,
        timeout=settings.hf_request_timeout_seconds,
    )
    # Inference Providers text_to_video returns the generated video as bytes.
    return client.text_to_video(prompt, model=model)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "LinkToon Studio API", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "provider": "huggingface-inference-providers",
        "provider_configured": str(bool(settings.hf_token)).lower(),
        "model": settings.hf_video_model,
    }


@app.post("/api/v1/jobs", status_code=202)
async def create_job(body: CreateJobRequest, request: Request) -> dict[str, Any]:
    require_client_key(request)
    if sum(1 for j in jobs.values() if j.get("status") in {"queued", "processing"}) >= 1:
        raise HTTPException(status_code=429, detail="Another video is already being generated. Wait for it to finish before submitting a new job.")
    if not settings.hf_token:
        raise HTTPException(status_code=503, detail="Hugging Face is not configured. Add HF_TOKEN as a secret on the backend host.")
    model = settings.hf_video_model.strip()
    if not model or "/" not in model:
        raise HTTPException(status_code=422, detail="Set HF_VIDEO_MODEL to a valid Hugging Face text-to-video model ID.")
    if body.model and body.model.strip() != model:
        raise HTTPException(status_code=422, detail="Model selection is controlled by the backend owner. Set HF_VIDEO_MODEL in Space settings.")
    if body.source_mode == "url" and not body.source_url:
        raise HTTPException(status_code=422, detail="Add a YouTube URL or switch to Topic only.")
    job_id = str(uuid4())
    job = {
        "id": job_id,
        "status": "queued",
        "prompt": body.prompt,
        "source_url": str(body.source_url) if body.source_url else None,
        "source_mode": body.source_mode,
        "model": model,
        "output_path": None,
        "output_url": None,
        "error": None,
        "created_at": now(),
        "updated_at": now(),
    }
    jobs[job_id] = job
    asyncio.create_task(run_job(job_id))
    return public_job(job)


async def run_job(job_id: str) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    try:
        job["status"] = "processing"
        job["updated_at"] = now()
        prompt = job["prompt"]
        if job["source_mode"] == "url":
            caption_text = await asyncio.to_thread(fetch_caption_context, job["source_url"])
            prompt = (
                prompt
                + "\n\nSOURCE TOPIC CONTEXT FROM PUBLIC YOUTUBE CAPTIONS (reference only):\n"
                + caption_text
                + "\n\nAdapt the core subject and key ideas into a new original cartoon story. Do not copy exact dialogue, scenes, footage, logos, or protected characters."
            )
        video_bytes = await asyncio.to_thread(generate_video_bytes, prompt, job["model"])
        if not video_bytes:
            raise RuntimeError("Hugging Face returned an empty video.")
        if len(video_bytes) > 250 * 1024 * 1024:
            raise RuntimeError("Generated video exceeded the 250 MB output limit.")
        output_path = settings.outputs_path / f"{job_id}.mp4"
        await asyncio.to_thread(output_path.write_bytes, video_bytes)
        job["output_path"] = str(output_path)
        job["output_url"] = f"/api/v1/jobs/{job_id}/output"
        job["status"] = "succeeded"
    except Exception as exc:
        message = str(exc)
        if job.get("source_mode") == "url":
            message = f"Could not process the source captions or generate the cartoon: {message}"
        elif "HF_TOKEN" not in message:
            message = f"Hugging Face generation failed: {message}"
        job["status"] = "failed"
        job["error"] = message[:1200]
    finally:
        job["updated_at"] = now()


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str, request: Request) -> dict[str, Any]:
    require_client_key(request)
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found. The in-memory job list resets when this backend restarts.")
    return public_job(job)


@app.get("/api/v1/jobs/{job_id}/output")
async def get_output(job_id: str) -> FileResponse:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    output_path = job.get("output_path")
    if job.get("status") != "succeeded" or not output_path or not Path(output_path).is_file():
        raise HTTPException(status_code=404, detail="The generated video is not available yet.")
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"linktoon-{job_id}.mp4",
    )
