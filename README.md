# MoneyPrinterTurbo — Ramiz's Video Studio

A cloud-deployment wrapper for [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), the open-source AI short-video generator.

## Deploy the public web app

**Deploy to Render:** [Open Render Blueprint deployment](https://render.com/deploy?repo=https://github.com/RamizUddin404/video-tool-suite)

The blueprint uses the upstream published Docker image and runs the Streamlit WebUI as a cloud web service. Render will ask you to sign in, review the service plan, and confirm deployment. This repository does not include a prebuilt APK.

- Deployment configuration: [render.yaml](render.yaml)
- Cloud deployment and security notes: [DEPLOYMENT.md](DEPLOYMENT.md)
- Upstream project: [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)
- Upstream MIT license: [UPSTREAM-LICENSE](UPSTREAM-LICENSE)

## Features from the upstream project

- Generate short videos from a topic or keywords.
- AI script generation through configured model providers.
- Stock footage, voice-over, subtitles, background music, and video rendering.
- WebUI, API, and CLI (the API and CLI are available in the upstream application; this Render Blueprint exposes the WebUI).

Some model, voice, and media providers require their own API keys. Edge TTS can work without a key. Video generation can consume paid API quota and substantial CPU/RAM.

## Public deployment: read before configuring keys

The deployed web UI is public. **Do not configure paid API keys or private credentials on a publicly accessible instance unless you have added and tested an access-control layer.** An unknown visitor may be able to submit jobs that consume configured provider quota. Never commit secrets, `config.toml`, or generated videos to this repository.

Render plan availability, persistent disk pricing, and resource limits can change. Review the cost shown by Render before confirming deployment. Video rendering may require a larger instance.

## Local development

For a full local install, follow the upstream instructions:
https://github.com/harry0703/MoneyPrinterTurbo#readme

Python 3.11+ and FFmpeg/media dependencies are required for source deployments. Android/Termux is not an officially supported deployment target and some native dependencies may not work there.

## Attribution

This repository is a deployment wrapper, not a fork containing the full upstream source. MoneyPrinterTurbo is maintained by its upstream author and distributed under MIT. Preserve its notices when redistributing substantial portions. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE). This wrapper is not affiliated with or endorsed by the upstream author.
