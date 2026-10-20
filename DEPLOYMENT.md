# Cloud deployment

## Public website and manual editor

GitHub Pages serves the static website and [browser-based editor](editor.html). The editor processes local video in the browser and can trim by start/end time, set 16:9 / 9:16 / 1:1 framing, apply visual filters, overlay text, burn in SRT subtitles, mix background music, and export a WebM recording.

Rendering uses browser Canvas and MediaRecorder in real time. Keep the page open during export. Browser support and device performance vary; the editor does not currently export MP4.

## Deploy the AI video engine on Render

1. Sign in to Render and open the Blueprint deploy flow.
2. Choose this repository: https://github.com/RamizUddin404/video-tool-suite
3. Review the `render.yaml` plan, disk, and region, then create the service.
4. Wait for the upstream image to start; open the public `onrender.com` URL.
5. Paste that HTTPS URL into the AI video generator panel in [editor.html](editor.html).
6. Configure provider keys only after reviewing the security notes below.

GitHub Pages cannot run Python, FFmpeg, or long-running AI video jobs. The Render Blueprint uses the upstream published MoneyPrinterTurbo container image and exposes its Streamlit WebUI on port 8501. It provisions a persistent disk for generated task files.

## Public-access security

This service is configured as a public web service. Do not enter personal, shared, or paid API credentials into a public instance unless you have separately protected access to it. Anyone who can reach the UI may be able to submit generation jobs and consume configured provider quota. Do not put secrets in this repository or GitHub Actions logs.

Render's plan and disk may incur charges. Review the provider's billing page before confirming deployment. Video rendering is resource-intensive; a larger instance may be required.

## Upstream source and license

AI generation is provided by the upstream project:
https://github.com/harry0703/MoneyPrinterTurbo

Upstream license: MIT, copyright (c) 2024 Harry. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE). This deployment wrapper and separate browser editor are not affiliated with or endorsed by the upstream author.
