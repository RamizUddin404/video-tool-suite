"""Minimal Replicate adapter. The selected model's input schema is model-specific."""
from typing import Any
import httpx
from .config import settings

API_BASE = "https://api.replicate.com/v1"

class ProviderConfigurationError(RuntimeError):
    pass

class ReplicateProvider:
    def _headers(self) -> dict[str, str]:
        if not settings.replicate_api_token or not settings.replicate_model_version:
            raise ProviderConfigurationError("AI provider is not configured. Set REPLICATE_API_TOKEN and REPLICATE_MODEL_VERSION on the backend host.")
        return {"Authorization": f"Bearer {settings.replicate_api_token}", "Content-Type": "application/json", "Prefer": "wait=1"}

    async def create_prediction(self, prompt: str, inputs: dict[str, Any], webhook_url: str | None = None) -> dict[str, Any]:
        payload_inputs = dict(inputs)
        payload_inputs.setdefault("prompt", prompt)
        body: dict[str, Any] = {"version": settings.replicate_model_version, "input": payload_inputs}
        if webhook_url:
            body["webhook"] = webhook_url
            body["webhook_events_filter"] = ["completed"]
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{API_BASE}/predictions", headers=self._headers(), json=body)
            if response.status_code >= 400:
                raise RuntimeError(f"Provider rejected the request (HTTP {response.status_code}): {response.text[:1000]}")
            return response.json()

    async def get_prediction(self, prediction_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{API_BASE}/predictions/{prediction_id}", headers=self._headers())
            if response.status_code >= 400:
                raise RuntimeError(f"Provider status check failed (HTTP {response.status_code}): {response.text[:500]}")
            return response.json()

def first_output_url(output: Any) -> str | None:
    if isinstance(output, str) and output.startswith(("https://", "http://")):
        return output
    if isinstance(output, list):
        for item in output:
            found = first_output_url(item)
            if found:
                return found
    if isinstance(output, dict):
        for value in output.values():
            found = first_output_url(value)
            if found:
                return found
    return None
