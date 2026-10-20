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

LinkToon contains a static website and a FastAPI backend. The backend submits video jobs to OpenRouter's asynchronous `/api/v1/videos` API, checks status, and stores the generated MP4 temporarily.

## Deploy your personal backend

Create a **Docker Space** in your Hugging Face account named **LinkToon-API**. The website is preset to the planned URL:

`https://ramiz404-linktoon-api.hf.space`

That URL only works after you create the Space and deploy this repository's root `Dockerfile` and `backend/` directory. The connected GitHub integration can edit this repository but cannot create a Space in your Hugging Face account.

In Space Settings → Variables and secrets, add:

- `OPENROUTER_API_KEY`: your OpenRouter API key.
- `APP_API_KEY`: a separate long, random private key for the website to authenticate to your backend.
- `OPENROUTER_VIDEO_MODEL`: defaults to `google/veo-3.1`.
- `ALLOWED_ORIGINS`: `https://ramizuddin404.github.io`.

Keep both keys in backend secrets only. Never put the OpenRouter key into public HTML or commit it to GitHub. In Creator Studio, enter the Space URL and the same `APP_API_KEY`.

After the Space build finishes, test `https://ramiz404-linktoon-api.hf.space/health`.

## Features and limits

- Topic mode submits a new cartoon-style video prompt to the configured OpenRouter video model.
- YouTube link mode tries to read public captions and uses them as context. If captions are unavailable, enter the topic or a transcript summary manually.
- Video generation is asynchronous: the backend submits a job, polls for completion, and downloads the result.
- Supported durations, aspect ratios, audio options, pricing, and model availability vary. This starter sends the model's default generation parameters; duration and ratio selections are prompt guidance, not guaranteed output settings. See the [OpenRouter video API docs](https://openrouter.ai/docs/api/api-reference/video-generation/create-videos) and [video model list](https://openrouter.ai/collections/video-models/).
- Generation may spend OpenRouter credits. Check current model pricing before submitting a job.
- Jobs and MP4 files are stored in memory and temporary local storage; restarting the Space can clear them. Only one job is accepted at a time.
- Link mode uses available captions rather than copying the source footage. Adapt topics into original stories and use material you have permission to adapt.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set OPENROUTER_API_KEY and APP_API_KEY locally; never commit real values.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Website: https://ramizuddin404.github.io/video-tool-suite/
Source repository: https://github.com/RamizUddin404/video-tool-suite
