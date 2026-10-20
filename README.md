# MoneyPrinterTurbo — Ramiz's Video Studio

A personal setup of [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo), an open-source AI short-video generation project.

> This repository is a setup/launch companion, not a rewrite or a bundled copy of the upstream source. See upstream for the full application, releases, screenshots, and complete feature list.

## What it does

MoneyPrinterTurbo can generate short videos from a topic or keywords: script, stock footage, voice-over, subtitles, background music, and a rendered video. Upstream offers a Streamlit WebUI, an API, and a CLI.

- WebUI and API run on a Python server; they are not a standalone Android APK.
- Python 3.11+ is required; the upstream recommended source setup uses `uv`.
- Online AI/model, stock-media, and speech providers may require API keys. Edge TTS is available without a key.
- FFmpeg/media dependencies and memory requirements depend on the chosen workflow.

## Quick start (Linux/macOS/Termux environment)

The upstream project targets desktop/server Linux, macOS, and Windows. Android/Termux is not an officially supported deployment target, so native media dependencies may fail on some phones.

```bash
pkg update
pkg install git python ffmpeg rust clang make cmake
python -m pip install --upgrade pip uv
git clone https://github.com/harry0703/MoneyPrinterTurbo.git
cd MoneyPrinterTurbo
uv python install 3.11
uv sync --frozen
uv run streamlit run webui/Main.py --server.address 127.0.0.1 --server.port 8501
```

If the command above fails due to a platform-specific dependency, use a Linux server/PC or the upstream Docker instructions instead. On desktop/server, follow the current upstream README exactly: https://github.com/harry0703/MoneyPrinterTurbo#readme

Then open `http://127.0.0.1:8501` in the same device's browser.

## API server / CLI

From the upstream repository root:

```bash
uv run python main.py
uv run python cli.py --help
```

## Configuration

Start the WebUI and enter API keys for the providers you want to use in its settings. Do not commit API keys, `config.toml`, generated videos, or other secrets to GitHub. Keep credentials local.

## Build / CI

GitHub Actions runs a lightweight Python syntax check and validates the repository setup. The full upstream app has heavy OS/media dependencies; this CI is not a guarantee that video rendering works on Android.

## Upstream and license

- Source: https://github.com/harry0703/MoneyPrinterTurbo
- License: MIT; upstream copyright and license notices must be retained when redistributing substantial portions.
- This companion repository is independently maintained and is not affiliated with or endorsed by the upstream author.

