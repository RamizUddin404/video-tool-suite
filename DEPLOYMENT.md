# Deployment guide — Ramiz Studio

## 1. Static website

1. Open repository **Settings → Pages**.
2. Select **GitHub Actions** as the build/deployment source.
3. Push to `main`; the workflow validates the website and deploys it.
4. Check the Actions tab for the real workflow result before sharing the URL.

GitHub Pages hosts only HTML/CSS/JavaScript. It cannot run Python API endpoints.

## 2. FastAPI backend

Deploy `backend/` to a Python host that supports ASGI. Install `backend/requirements.txt` and use a start command equivalent to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these environment variables in the host dashboard, never in website source:

- `REPLICATE_API_TOKEN`: provider token
- `REPLICATE_MODEL_VERSION`: selected model version identifier
- `ALLOWED_ORIGINS`: exact public website origin, e.g. `https://ramizuddin404.github.io`

The selected provider model must accept the input schema sent by the user. Check provider pricing, model licensing, output handling and account limits before enabling requests.

## 3. Connect the editor

Open `editor.html`, enter the deployed backend base URL and use the AI generation panel. The UI calls `POST /api/v1/jobs` and polls `GET /api/v1/jobs/{job_id}`. A working generation requires valid provider credentials and a compatible model version. Without configuration, the API deliberately returns an actionable error.

## 4. Production hardening required

The current backend is a development scaffold. It uses in-memory job state and does not provide user accounts, a durable queue, quotas, persistent media storage or abuse controls. Before public production, add authentication, rate limits, durable job storage/queue, provider cost limits, cancellation, secure output delivery, retention/deletion policies and monitoring. Do not run a public unauthenticated endpoint with an unrestricted paid provider token.
