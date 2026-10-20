from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from fastapi import FastAPI, HTTPException
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
