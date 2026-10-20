from __future__ import annotations
import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from youtube_transcript_api import YouTubeTranscriptApi

from .config import settings
from .provider import HuggingFaceVideoProvider, ProviderConfigurationError
from .schemas import CreateJobRequest

settings.outputs_path
app = FastAPI(title="LinkToon Studio API", version="1.0.0", description="Self-managed FastAPI backend using Hugging Face Inference Providers.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
app.mount("/outputs", StaticFiles(directory=str(settings.outputs_path)), name="outputs")
provider = HuggingFaceVideoProvider()
jobs: dict[str, dict[str, Any]] = {}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {key: job.get(key) for key in ("id", "status", "prompt", "output_url", "error", "created_at", "updated_at")}

def youtube_id(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower().split(":")[0]
    if host in {"youtu.be", "www.youtu.be"}:
        return parsed.path.strip("/").split("/")[0] or None
    if host.endswith("youtube.com") or host == "youtube-nocookie.com":
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        match = re.match(r"^/(?:shorts|embed|live)/([^/?]+)", parsed.path)
        if match:
            return match.group(1)
    return None

def source_context(url: str) -> str:
    video_id = youtube_id(url)
    if not video_id:
        raise ValueError("For link-based topic extraction, provide a YouTube link with accessible captions. Other URL types are not downloaded by this backend.")
    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(str(item.text) for item in transcript)
    except Exception as exc:
        raise ValueError("Could not read captions for this YouTube video. Check that captions are available, then enter the topic manually. Details: " + str(exc)[:250]) from exc
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise ValueError("The video captions were empty. Enter the topic manually.")
    return text[:12000]

@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "LinkToon Studio API", "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "provider": "huggingface-inference-providers",
        "provider_configured": bool(settings.hf_token),
        "default_model": settings.hf_video_model,
        "note": "Video generation also requires the selected model/provider to support text-to-video for your account."
    }

@app.post("/api/v1/jobs", status_code=202)
async def create_job(body: CreateJobRequest) -> dict[str, Any]:
    if not settings.hf_token:
        raise HTTPException(status_code=503, detail="Hugging Face token missing. Set HF_TOKEN as a secret on the backend host.")
    prompt = body.prompt
    if body.source_mode == "url":
        if not body.source_url:
            raise HTTPException(status_code=400, detail="source_url is required when source_mode is url.")
        try:
            transcript = await asyncio.to_thread(source_context, str(body.source_url))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        prompt += "\n\nREFERENCE VIDEO CAPTION CONTEXT (adapt the topic; do not copy exact scenes/dialogue):\n" + transcript
    job_id = str(uuid4())
    job = {
        "id": job_id, "status": "queued", "prompt": prompt,
        "output_url": None, "error": None, "created_at": now(),
        "updated_at": now(), "model": body.model or settings.hf_video_model
    }
    jobs[job_id] = job
    asyncio.create_task(run_job(job_id, prompt, body.model, body.inputs))
    return public_job(job)

async def run_job(job_id: str, prompt: str, model: str | None, inputs: dict[str, Any]) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    job["status"] = "processing"
    job["updated_at"] = now()
    try:
        video_bytes = await asyncio.wait_for(
            asyncio.to_thread(provider.create_video, prompt, model, inputs),
            timeout=settings.hf_request_timeout_seconds
        )
        if not video_bytes:
            raise RuntimeError("Hugging Face returned an empty video.")
        output_path = settings.outputs_path / f"{job_id}.mp4"
        output_path.write_bytes(video_bytes)
        public_base = settings.public_base_url.rstrip("/")
        job["output_url"] = f"{public_base}/outputs/{job_id}.mp4" if public_base else f"/outputs/{job_id}.mp4"
        job["status"] = "succeeded"
    except (ProviderConfigurationError, Exception) as exc:
        job["status"] = "failed"
        job["error"] = str(exc)[:1200]
    finally:
        job["updated_at"] = now()

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found. Development backend stores jobs in memory; a restart clears job history.")
    return public_job(job)
