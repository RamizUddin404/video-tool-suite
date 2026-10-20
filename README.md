---
title: LinkToon Backend
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# LinkToon Studio

A self-managed FastAPI backend that uses Hugging Face Inference Providers to generate a new cartoon video from a prompt. For a YouTube source link, it tries to read accessible captions and uses them as topic context; it does not download or copy the source video.

## Files

- `index.html` and `editor.html`: static website for GitHub Pages.
- `backend/`: FastAPI backend, transcript extraction, video generation and output serving.
- `Dockerfile`: Docker Space deployment configuration.

## Deploy your own backend on Hugging Face

1. Create a **Docker Space** in your Hugging Face account.
2. Copy/push the root repository files, including `Dockerfile`, `README.md`, and `backend/`, into that Space.
3. Under Space Settings → Variables and secrets, set `HF_TOKEN` as a secret with Inference Providers permission.
4. Set `PUBLIC_BASE_URL` to the Space's final URL and `ALLOWED_ORIGINS=https://ramizuddin404.github.io`.
5. Once the Space is built, open its `/health` endpoint.
6. Paste the Space URL into the Creator Studio's backend URL field.

Hugging Face generates the Space URL only after the Space is created, so the final backend URL cannot be hardcoded beforehand. Do not put HF_TOKEN in this public GitHub repository or browser code.

## Backend settings

- `HF_TOKEN`: required secret.
- `HF_VIDEO_MODEL`: default `Wan-AI/Wan2.2-TI2V-5B`.
- `HF_PROVIDER`: default `fal-ai`.
- `ALLOWED_ORIGINS`: allowed browser origins.
- `PUBLIC_BASE_URL`: your final Space URL.
- `OUTPUT_DIR`: output folder, defaults to `/tmp/linktoon-outputs`.

The model is documented for text-to-video via Hugging Face Inference Providers, but model availability, provider access, quotas and pricing can change. Video inference may cost money. Job state and generated files are currently stored locally and may be lost when the Space restarts.

## Limitations

- Only YouTube links with accessible captions can be used as source context. If captions are unavailable, enter the topic manually.
- This generates a new video from text context; it does not recreate the reference video scene-for-scene.
- Duration and aspect ratio depend on the selected model/provider.
- Before a public launch, add authentication, rate limiting, quota controls, durable jobs and output retention.

Website: https://ramizuddin404.github.io/video-tool-suite/
Repository: https://github.com/RamizUddin404/video-tool-suite
