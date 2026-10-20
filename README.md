# MoneyPrinterTurbo — Ramiz's Video Studio

A public GitHub Pages website with a browser-based manual video editor plus a deployment path for [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), the upstream AI short-video generator.

## Website

After GitHub Pages deployment, open: **https://ramizuddin404.github.io/video-tool-suite/**

- [Manual video editor](editor.html): local video preview, trim range, 16:9 / 9:16 / 1:1 framing, visual filters, title overlays, SRT subtitles, background music and audio mixing, WebM export.
- [AI video generator connection](editor.html#ai): configure the URL of the deployed MoneyPrinterTurbo WebUI and open it.
- [GitHub Pages workflow](.github/workflows/pages.yml): deploys the static website automatically.

The manual editor uses browser Canvas and MediaRecorder. Export is WebM and renders in real time; keep the page open while exporting. Very large files may be slow on phones. Source media is processed in the browser rather than uploaded to this repository.

## Deploy the AI video engine

GitHub Pages cannot run Python, FFmpeg or long-running AI video jobs. Deploy the upstream container separately using the [Render Blueprint](render.yaml):

**[Deploy the public backend to Render](https://render.com/deploy?repo=https://github.com/RamizUddin404/video-tool-suite)**

Review the service plan, disk, region and pricing before confirming. After deployment, copy its HTTPS URL into the editor's AI video generator panel.

**Security:** do not configure paid API keys or private credentials on a publicly accessible backend unless you have added and tested access control. Visitors may otherwise consume provider quota. Never commit secrets or generated videos.

## Upstream features

MoneyPrinterTurbo supports topic/keyword-based short-video generation through its configured AI and media providers. Some providers require API keys and rendering can consume paid quota and CPU/RAM. The backend's available AI generation features depend on its own configuration.

## Attribution and license

MoneyPrinterTurbo is maintained by its upstream author and distributed under MIT. This repository is a wrapper plus a separate browser editor; it is not an official upstream fork. Preserve upstream notices when redistributing upstream code. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE). This repository is not affiliated with or endorsed by the upstream author.
