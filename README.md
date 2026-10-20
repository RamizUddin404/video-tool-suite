---
title: LinkToon Backend
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# LinkToon Studio

This repository contains the static website and its own FastAPI backend. The backend uses Hugging Face Inference Providers for text-to-video generation; it does not depend on another person's application server.

## Deploy your personal backend

Create a **Docker Space** in your Hugging Face account with the exact Space name **LinkToon-API**. The website is preconfigured for the expected endpoint:

`https://ramiz404-linktoon-api.hf.space`

That URL is only live after you create the Space and deploy this repository's Dockerfile. The currently connected Hugging Face integration has read-only repository permission, so this assistant can prepare the code but cannot create/publish the Space on your behalf.

Upload/copy the repository contents to the new Space, including the root `Dockerfile` and `backend/` directory. In **Space Settings → Variables and secrets**, set:

- `HF_TOKEN`: a Hugging Face user access token with **Inference Providers** permission.
- `APP_API_KEY`: a long, random private key of your choice. Enter the same value in LinkToon Creator Studio when you use the site.
- `HF_VIDEO_MODEL`: `Wan-AI/Wan2.2-TI2V-5B` (default).
- `HF_PROVIDER`: `fal-ai` (default).
- `ALLOWED_ORIGINS`: `https://ramizuddin404.github.io`.

Wait for the Space build to finish, then open `/health` on the Space URL. Paste/use the Space URL and your private access key in Creator Studio. Never put either secret into GitHub HTML or commit it to this repository.

## How it works and limits

- Text/topic mode sends a 3D-cartoon generation prompt to the configured Hugging Face text-to-video model.
- YouTube link mode tries to read available public captions and uses them as topic context. If captions are off, unavailable, or blocked, use Topic only mode and enter the subject/summary yourself.
- The generation model typically produces a short clip. The selected duration and aspect ratio are prompts, not guarantees; automatic 3-minute multi-scene assembly and narration are not implemented yet.
- Video inference may use paid quota/credits and depends on your token, model availability, provider limits and current pricing.
- Jobs and generated files are held in local in-memory/temporary storage. Restarting the Space can clear job status and outputs; this is a starter personal backend, not a durable multi-user production service.
- The backend requires a private `APP_API_KEY` and allows one generation job at a time to limit accidental spending.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set HF_TOKEN and APP_API_KEY in .env locally; never commit real values.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Website: https://ramizuddin404.github.io/video-tool-suite/
Source repository: https://github.com/RamizUddin404/video-tool-suite
