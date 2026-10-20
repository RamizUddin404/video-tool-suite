from __future__ import annotations

import asyncio
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from youtube_transcript_api import YouTubeTranscriptApi

from .config import settings
from .schemas import CreateJobRequest

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
app = FastAPI(title="LinkToon Studio API", version="0.3.0",
              description="Self-managed LinkToon backend using OpenRouter video generation.")
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
    return {key: job.get(key) for key in (
        "id", "status", "prompt", "output_url", "error", "created_at", "updated_at", "model"
    )}


def require_client_key(request: Request) -> None:
    expected = settings.app_api_key
    if not expected:
        raise HTTPException(status_code=503, detail="Set APP_API_KEY as a secret on the backend host.")
    supplied = request.headers.get("authorization", "")
    supplied = supplied[7:].strip() if supplied.lower().startswith("bearer ") else ""
    if not secrets.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid backend access key.")


def extract_youtube_id(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    host = (parsed.hostname or "").lower()
    allowed = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
               "youtube-nocookie.com", "www.youtube-nocookie.com"}
    if host not in allowed:
        raise ValueError("Link mode currently supports YouTube links with accessible captions. Otherwise use Topic only.")
    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    else:
        match = re.match(r"^/(?:shorts|embed|live)/([^/?]+)", parsed.path)
        video_id = match.group(1) if match else ""
    if not VIDEO_ID_RE.fullmatch(video_id):
        raise ValueError("Could not identify a valid YouTube video ID.")
    return video_id


def fetch_caption_context(raw_url: str) -> str:
    video_id = extract_youtube_id(raw_url)
    transcript = YouTubeTranscriptApi().fetch(video_id, languages=["bn", "en", "hi"])
    parts: list[str] = []
    total = 0
    for snippet in transcript.snippets:
        piece = " ".join(str(snippet.text).split())[:max(0, 7000 - total)]
        if not piece:
            break
        parts.append(piece)
        total += len(piece)
    if not parts:
        raise ValueError("No accessible captions found. Enter the video topic manually.")
    return " ".join(parts)


def openrouter_headers() -> dict[str, str]:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured on the backend host.")
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ramizuddin404.github.io/video-tool-suite/",
        "X-OpenRouter-Title": "LinkToon Studio",
    }


async def submit_video(prompt: str, model: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{OPENROUTER_BASE}/videos",
            headers=openrouter_headers(),
            json={"model": model, "prompt": prompt},
        )
    if response.is_error:
        try:
            detail = response.json().get("error", {}).get("message") or response.text
        except Exception:
            detail = response.text
        raise RuntimeError(f"OpenRouter request failed ({response.status_code}): {str(detail)[:800]}")
    data = response.json()
    if not data.get("id"):
        raise RuntimeError("OpenRouter did not return a video job ID.")
    return data


async def run_job(job_id: str) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    try:
        job["status"] = "processing"
        job["updated_at"] = now()
        prompt = job["prompt"]
        if job["source_mode"] == "url":
            captions = await asyncio.to_thread(fetch_caption_context, job["source_url"])
            prompt += (
                "\n\nSOURCE TOPIC CONTEXT FROM PUBLIC YOUTUBE CAPTIONS:\n" + captions
                + "\n\nCreate a fresh original cartoon interpretation. Do not copy exact dialogue, scenes, footage, logos, or protected characters."
            )
        remote = await submit_video(prompt, job["model"])
        remote_id = remote["id"]
        deadline = asyncio.get_running_loop().time() + settings.request_timeout_seconds
        async with httpx.AsyncClient(timeout=90) as client:
            while asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(8)
                poll = await client.get(f"{OPENROUTER_BASE}/videos/{remote_id}", headers=openrouter_headers())
                if poll.is_error:
                    raise RuntimeError(f"OpenRouter status request failed ({poll.status_code}): {poll.text[:400]}")
                state = poll.json()
                status = str(state.get("status", "")).lower()
                job["updated_at"] = now()
                if status in {"failed", "error", "cancelled"}:
                    raise RuntimeError(str(state.get("error") or "Video generation failed.")[:800])
                if status in {"completed", "succeeded", "success"} or state.get("unsigned_urls"):
                    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds, follow_redirects=True) as dl:
                        download = await dl.get(
                            f"{OPENROUTER_BASE}/videos/{remote_id}/content",
                            headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                        )
                        if download.is_error and state.get("unsigned_urls"):
                            download = await dl.get(state["unsigned_urls"][0])
                        download.raise_for_status()
                    if not download.content:
                        raise RuntimeError("OpenRouter returned an empty video.")
                    if len(download.content) > 250 * 1024 * 1024:
                        raise RuntimeError("Generated video exceeded the 250 MB output limit.")
                    output = settings.outputs_path / f"{job_id}.mp4"
                    await asyncio.to_thread(output.write_bytes, download.content)
                    job["output_path"] = str(output)
                    job["output_url"] = f"/api/v1/jobs/{job_id}/output"
                    job["status"] = "succeeded"
                    return
                if status not in {"", "pending", "queued", "processing", "running"}:
                    raise RuntimeError(f"Unexpected OpenRouter job status: {status}")
        raise RuntimeError("Timed out waiting for OpenRouter video generation.")
    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)[:1200]
    finally:
        job["updated_at"] = now()


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "LinkToon Studio API", "docs": "/docs", "health": "/health"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
        "provider": "openrouter",
        "provider_configured": str(bool(settings.openrouter_api_key)).lower(),
        "model": settings.openrouter_video_model,
    }


@app.post("/api/v1/jobs", status_code=202)
async def create_job(body: CreateJobRequest, request: Request) -> dict[str, Any]:
    require_client_key(request)
    if not settings.openrouter_api_key:
        raise HTTPException(status_code=503, detail="Add OPENROUTER_API_KEY as a backend secret.")
    if any(item.get("status") in {"queued", "processing"} for item in jobs.values()):
        raise HTTPException(status_code=429, detail="Another video is already generating. Wait for it to finish.")
    model = settings.openrouter_video_model.strip()
    if not model:
        raise HTTPException(status_code=503, detail="Set OPENROUTER_VIDEO_MODEL in backend settings.")
    if body.model and body.model.strip() != model:
        raise HTTPException(status_code=422, detail="Video model is controlled by the backend owner.")
    if body.source_mode == "url" and not body.source_url:
        raise HTTPException(status_code=422, detail="Add a YouTube URL or choose Topic only.")
    job_id = str(uuid4())
    jobs[job_id] = {
        "id": job_id, "status": "queued", "prompt": body.prompt,
        "source_url": str(body.source_url) if body.source_url else None,
        "source_mode": body.source_mode, "model": model, "output_path": None,
        "output_url": None, "error": None, "created_at": now(), "updated_at": now(),
    }
    asyncio.create_task(run_job(job_id))
    return public_job(jobs[job_id])


@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str, request: Request) -> dict[str, Any]:
    require_client_key(request)
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found. In-memory jobs reset when the backend restarts.")
    return public_job(job)


@app.get("/api/v1/jobs/{job_id}/output")
async def get_output(job_id: str) -> FileResponse:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    path = job.get("output_path")
    if job.get("status") != "succeeded" or not path or not Path(path).is_file():
        raise HTTPException(status_code=404, detail="Generated video is not available yet.")
    return FileResponse(path, media_type="video/mp4", filename=f"linktoon-{job_id}.mp4")
