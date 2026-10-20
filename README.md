# Ramiz Studio

An independent personal video studio by **RamizUddin404**. The website and interface are original project code, maintained independently.

## Project structure

- `index.html` — responsive, classic dark-and-gold landing page with CSS 3D motion.
- `editor.html` — browser-based local editor and AI-job submission interface.
- `backend/` — FastAPI service with bounded video uploads, provider adapter boundary, job validation, and status polling.
- `.github/workflows/pages.yml` — validates and deploys the static website to GitHub Pages.

## Current feature status

| Feature | Status |
|---|---|
| Homepage and responsive 3D styling | Implemented in HTML/CSS |
| Local video preview and basic editing/export | Browser-dependent; test in a modern browser |
| AI job API endpoints | Implemented as backend scaffolding |
| Actual AI generation | **Requires a configured provider model, API token, backend deployment and provider-specific inputs** |
| Durable job queue and multi-user production auth | Not included yet |
| MP4 export from the browser editor | Not included; browser export is WebM where supported |

Do not place provider API tokens in HTML, GitHub Pages, or client-side JavaScript.

## Run the backend locally

Python 3.11+ recommended.

```bash
cd backend
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/health` and `http://127.0.0.1:8000/docs`.

### Configure an AI provider

The initial adapter targets the Replicate predictions and file-upload APIs. Set these **on the backend host only**:

- `REPLICATE_API_TOKEN`
- `REPLICATE_MODEL_VERSION` — a model version hash supported by your account
- `ALLOWED_ORIGINS` — comma-separated exact origins allowed to call the API

The model's input schema varies. Submit a JSON `inputs` object matching the selected model's documented schema. The editor can upload a video to the provider's temporary file storage and place its returned URL in the chosen model input field. A normal watch-page URL may not work; many models require a direct media URL or a supported uploaded-file URL. Without valid credentials and a model version, generation deliberately returns a clear configuration error; it does not fake a successful video.

**Cost and licensing:** the website code is free to run, but provider inference and hosting may cost money and are not guaranteed free. Do not describe every generated result as copyright-free. Use material you own, public-domain media, or assets whose licenses explicitly permit your intended use; retain required attribution.

The first implementation keeps job state in process memory and polls the provider. It is suitable as a development scaffold, not a multi-worker production deployment. Add durable storage, a task queue, authentication, rate limits, quota controls, retention policy and output-file handling before public launch.

## Deploy the website

Enable GitHub Pages for the repository using **GitHub Actions** as the source. The workflow validates the static files and publishes the site on pushes to `main`.

Expected URL: `https://ramizuddin404.github.io/video-tool-suite/`

GitHub Pages serves static files only; it does not run the FastAPI backend. Deploy `backend/` to a Python-capable host separately, then set that backend's exact URL in the editor. Do not expose API secrets in the public website.

## License

Original code in this repository is provided under the MIT License in `LICENSE`. Third-party packages and hosted model providers retain their own licenses and terms. No upstream MoneyPrinterTurbo application code is required by this project.
