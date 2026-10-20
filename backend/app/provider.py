"""Hugging Face Inference Providers adapter for text-to-video generation."""
from __future__ import annotations
from typing import Any
from huggingface_hub import InferenceClient
from .config import settings

class ProviderConfigurationError(RuntimeError):
    pass

class HuggingFaceVideoProvider:
    def _client(self, model: str | None = None) -> InferenceClient:
        if not settings.hf_token:
            raise ProviderConfigurationError(
                "Hugging Face is not configured. Add HF_TOKEN as a secret on the backend host."
            )
        return InferenceClient(
            provider=settings.hf_provider,
            model=model or settings.hf_video_model,
            token=settings.hf_token,
            timeout=settings.hf_request_timeout_seconds,
        )

    def create_video(self, prompt: str, model: str | None = None, inputs: dict[str, Any] | None = None) -> bytes:
        """Generate a video and return MP4 bytes. Model/provider must support text_to_video."""
        client = self._client(model)
        options = dict(inputs or {})
        # Keep only options intended as documented generation parameters; prompt is authoritative.
        result = client.text_to_video(prompt=prompt, **options)
        if isinstance(result, bytes):
            return result
        if hasattr(result, "read"):
            return result.read()
        raise RuntimeError("Hugging Face provider returned an unsupported video response.")
