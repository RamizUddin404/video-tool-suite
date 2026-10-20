from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl


class CreateJobRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=4000)
    model: str | None = Field(default=None, min_length=3, max_length=200)
    source_url: HttpUrl | None = None
    source_mode: Literal["url", "topic"] = "topic"
    inputs: dict[str, Any] = Field(default_factory=dict, description="Reserved for harmless model options; arbitrary source URLs are not passed to text-to-video models.")


class JobResponse(BaseModel):
    id: str
    status: Literal["queued", "processing", "succeeded", "failed"]
    prompt: str
    output_url: str | None = None
    error: str | None = None
    created_at: str
    updated_at: str
