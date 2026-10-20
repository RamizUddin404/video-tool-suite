# Deployment guide — Ramiz Studio

## 1. Static website

1. Open the repository's **Settings → Pages**.
2. Select **GitHub Actions** as the build and deployment source.
3. Push to `main`; the workflow validates the site and deploys it.
4. Check the Actions tab for the real workflow result before sharing the URL.

GitHub Pages hosts only the HTML/CSS/JavaScript frontend. It cannot run Python API endpoints.

## 2. FastAPI backend

Deploy the `backend/` directory to a Python host that supports ASGI. Install `backend/requirements.txt` and use a start command equivalent to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables in the host dashboard, never in the website source:

- `REPLICATE_API_TOKEN`: provider token
- `REPLICATE_MODEL_VERSION`: selected model version identifier
- `ALLOWED_ORIGINS`: the exact public Pages origin, for example `https://ramizuddin404.github.io`

The selected provider model must accept the input schema sent by the user. Check provider pricing, model licensing, output handling and account limits before enabling public requests.

## 3. Connect the editor

Open `editor.html`, enter the deployed backend's base URL, and use the AI generation panel. The UI calls `POST /api/v1/jobs` and polls `GET /api/v1/jobs/{job_id}`. A working generation requires valid backend configuration. If the backend is not deployed or configured, generation will fail visibly; the UI must not claim it succeeded.

## 4. Production hardening required

The current backend scaffold uses in-memory job state and does not provide user accounts, a durable queue, quotas or persistent media storage. Before public production, add authentication, rate limiting, durable job storage/queue, provider cost limits, job cancellation, secure output delivery, retention/deletion policies, monitoring and abuse controls. Do not run a public unauthenticated endpoint with an unrestricted paid provider token.
