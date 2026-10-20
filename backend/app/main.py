from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from pathlib import Path
import os
import tempfile
from typing import Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .provider import ReplicateProvider, first_output_url
from .schemas import CreateJobRequest

app = FastAPI(title="Ramiz Studio API", version="0.1.0", description="Independent video-generation API scaffold.")
app.add_middleware(CORSMiddleware, allow_origins=settings.origins, allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
provider = ReplicateProvider()
jobs: dict[str, dict[str, Any]] = {}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def public_job(job: dict[str, Any]) -> dict[str, Any]:
    return {key: job.get(key) for key in ("id", "status", "prompt", "output_url", "error", "created_at", "updated_at")}

@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "Ramiz Studio API", "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider_configured": str(bool(settings.replicate_api_token and settings.replicate_model_version)).lower()}

@app.post("/api/v1/source/upload")
async def upload_source_video(file: UploadFile = File(...)) -> dict[str, Any]:
    """Upload a user-selected video to the configured provider's temporary file storage."""
    if not settings.replicate_api_token or not settings.replicate_model_version:
        raise HTTPException(status_code=503, detail="Provider file upload requires REPLICATE_API_TOKEN and REPLICATE_MODEL_VERSION on the backend host.")
    if not (file.content_type or "").lower().startswith("video/"):
        raise HTTPException(status_code=415, detail="Upload a video file with a recognized video content type.")
    safe_name = Path(file.filename or "source-video").name[:180]
    suffix = Path(safe_name).suffix[:12]
    temp_path = None
    total = 0
    try:
        with tempfile.NamedTemporaryFile(prefix="ramiz-source-", suffix=suffix, delete=False) as temp:
            temp_path = temp.name
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > 100 * 1024 * 1024:
                    raise HTTPException(status_code=413, detail="Video files must be 100 MB or smaller.")
                temp.write(chunk)
        if total == 0:
            raise HTTPException(status_code=400, detail="The uploaded video file is empty.")
        with open(temp_path, "rb") as stream:
            async with httpx.AsyncClient(timeout=180) as client:
                response = await client.post(
                    "https://api.replicate.com/v1/files",
                    headers={"Authorization": f"Bearer {settings.replicate_api_token}"},
                    files={"content": (safe_name, stream, file.content_type or "application/octet-stream")},
                )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Provider upload failed (HTTP {response.status_code}): {response.text[:600]}")
        result = response.json()
        file_url = (result.get("urls") or {}).get("get")
        if not file_url:
            raise HTTPException(status_code=502, detail="Provider accepted the upload but did not return a file URL.")
        return {"file_id": result.get("id"), "file_url": file_url, "filename": safe_name, "size": total, "expires_at": result.get("expires_at"), "note": "The selected model must accept this uploaded file URL as an input."}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not upload source video: {str(exc)[:400]}")
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

@app.post("/api/v1/jobs", status_code=202)
async def create_job(body: CreateJobRequest) -> dict[str, Any]:
    if not settings.replicate_api_token or not settings.replicate_model_version:
        raise HTTPException(status_code=503, detail="AI provider is not configured. Set REPLICATE_API_TOKEN and REPLICATE_MODEL_VERSION on the backend host.")
    job_id = str(uuid4())
    job = {"id": job_id, "status": "processing", "prompt": body.prompt, "inputs": body.inputs, "output_url": None, "error": None, "created_at": now(), "updated_at": now(), "provider_id": None}
    jobs[job_id] = job
    asyncio.create_task(run_job(job_id, body.prompt, body.inputs, str(body.webhook_url) if body.webhook_url else None))
    return public_job(job)

async def run_job(job_id: str, prompt: str, inputs: dict[str, Any], webhook_url: str | None) -> None:
    job = jobs.get(job_id)
    if not job:
        return
    try:
        prediction = await provider.create_prediction(prompt, inputs, webhook_url)
        job["provider_id"] = prediction.get("id")
        status = prediction.get("status", "starting")
        started = asyncio.get_running_loop().time()
        while status not in ("succeeded", "failed", "canceled"):
            if asyncio.get_running_loop().time() - started > settings.job_timeout_seconds:
                raise TimeoutError("Provider job timed out.")
            await asyncio.sleep(max(1.0, settings.provider_poll_seconds))
            prediction = await provider.get_prediction(job["provider_id"])
            status = prediction.get("status", "processing")
            job["updated_at"] = now()
        if status == "succeeded":
            output_url = first_output_url(prediction.get("output"))
            if not output_url:
                raise RuntimeError("Provider reported success but returned no recognizable output URL.")
            job["status"] = "succeeded"
            job["output_url"] = output_url
        else:
            job["status"] = "failed"
            job["error"] = str(prediction.get("error") or f"Provider job ended with status: {status}")[:1200]
    except Exception as exc:
        job["status"] = "failed"
        job["error"] = str(exc)[:1200]
    finally:
        job["updated_at"] = now()

@app.get("/api/v1/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found. In-memory jobs disappear when the backend restarts.")
    return public_job(job)
