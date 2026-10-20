---
title: LinkToon Backend
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# LinkToon Studio

Static website plus a FastAPI backend that requests text-to-video generation from Hugging Face Inference Providers.

## Deploy your own backend

1. Create a **Docker Space** in your Hugging Face account.
2. Copy the root repository files (including `Dockerfile` and `backend/`) into that Space.
3. In Space Settings → Variables and secrets, add `HF_TOKEN` as a secret with Inference Providers permission.
4. Set `PUBLIC_BASE_URL` to your Space's final URL and `ALLOWED_ORIGINS=https://ramizuddin404.github.io`.
5. Wait for the Space to build and test its `/health` endpoint.
6. Paste the Space URL into the Creator Studio's backend URL field.

Hugging Face creates the permanent Space URL after the Space is created, so it cannot be hardcoded before then. Never put the token in browser JavaScript or this public GitHub repository.

## Environment

- `HF_TOKEN`: required secret.
- `HF_VIDEO_MODEL`: default `Wan-AI/Wan2.2-TI2V-5B`.
- `HF_PROVIDER`: default `fal-ai`.
- `PUBLIC_BASE_URL`: final Space URL.
- `ALLOWED_ORIGINS`: allowed website origins.
- `OUTPUT_DIR`: output folder, default `/tmp/linktoon-outputs`.

For YouTube links, the backend reads accessible captions and uses them as context. If captions are unavailable, enter the topic manually. It creates a new video from text context, not a scene-for-scene copy. Model access, quota, pricing and supported controls depend on the provider. Jobs and generated files currently use local storage and may be lost on restart.

Website: https://ramizuddin404.github.io/video-tool-suite/
Repository: https://github.com/RamizUddin404/video-tool-suite
