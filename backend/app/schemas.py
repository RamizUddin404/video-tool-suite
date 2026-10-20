from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl

class CreateJobRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=4000)
    inputs: dict[str, Any] = Field(default_factory=dict, description="Provider-specific input fields; must match the selected model schema.")
    webhook_url: HttpUrl | None = None

class JobResponse(BaseModel):
    id: str
    status: Literal["queued", "processing", "succeeded", "failed"]
    prompt: str
    output_url: str | None = None
    error: str | None = None
    created_at: str
    updated_at: str
