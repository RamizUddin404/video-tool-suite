# MoneyPrinterTurbo — Ramiz's Video Studio

A public GitHub Pages launchpad and cloud deployment wrapper for [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), the open-source AI short-video generator.

## Public website (GitHub Pages)

The static front end is in [index.html](index.html). GitHub Actions deploys it to GitHub Pages when the site files change. After the first successful run, the public URL is normally:

**https://ramizuddin404.github.io/video-tool-suite/**

If Pages has not been enabled for this repository yet, open **Settings → Pages** and select **GitHub Actions** as the build and deployment source, then run the workflow from the Actions tab.

## Deploy the video engine

GitHub Pages only hosts static files; it cannot run Python, FFmpeg, the Streamlit WebUI, or video-rendering jobs. The backend blueprint uses the upstream published Docker image on Render:

**[Deploy the public backend to Render](https://render.com/deploy?repo=https://github.com/RamizUddin404/video-tool-suite)**

Review the service plan, persistent disk, region and costs before confirming deployment. Once the backend is live, paste its HTTPS URL into the GitHub Pages site and select **Open hosted studio**.

- Website: [index.html](index.html)
- Backend deployment configuration: [render.yaml](render.yaml)
- Deployment and security notes: [DEPLOYMENT.md](DEPLOYMENT.md)
- Upstream project: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)
- Upstream MIT license: [UPSTREAM-LICENSE](UPSTREAM-LICENSE)

## Features from the upstream project

- Generate short videos from a topic or keywords.
- AI script generation through configured model providers.
- Stock footage, voice-over, subtitles, background music, and video rendering.
- WebUI, API, and CLI are available in the upstream application; the Render Blueprint is intended to expose the WebUI.

Some model, voice, and media providers require API keys. Edge TTS may work without a key. Video generation can consume paid API quota and substantial CPU/RAM.

## Public deployment security

**Do not configure paid API keys or private credentials on a publicly accessible instance unless you have added and tested access control.** Unknown visitors may submit jobs that consume provider quota. Never commit secrets, config files, or generated videos to this repository.

## Attribution and license

This repository is a deployment wrapper and static launchpad, not a fork containing the full upstream source. MoneyPrinterTurbo is maintained by its upstream author and distributed under MIT. Preserve its copyright and license notices when redistributing substantial portions. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE). This repository is not affiliated with or endorsed by the upstream author.
