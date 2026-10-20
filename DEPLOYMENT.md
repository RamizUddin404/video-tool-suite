# Cloud deployment

## Deploy on Render

1. Sign in to Render and open the Blueprint deploy flow.
2. Choose this repository: https://github.com/RamizUddin404/video-tool-suite
3. Review the `render.yaml` plan and region, then create the service.
4. Wait for the upstream image to start; open the public `onrender.com` URL.
5. Configure provider keys only after reviewing the security notes below.

The Blueprint uses the upstream published container image, not a locally built Android app. It exposes the upstream Streamlit WebUI on port 8501 and provisions a persistent disk for generated task files.

## Public-access security

This service is configured as a public web service. Do not enter personal, shared, or paid API credentials into a public instance unless you have separately protected access to it. Anyone who can reach the UI may be able to submit generation jobs and consume configured provider quota. Do not put secrets in this repository or GitHub Actions logs.

Render's free services may sleep and have limited resources; this Blueprint selects the Starter plan and provisions a persistent disk, which may incur charges under Render's current pricing. Review the provider's billing page before confirming deployment. Video rendering is resource-intensive; a larger instance may be required.

## Upstream source and license

Application source and container image belong to the upstream project:
https://github.com/harry0703/MoneyPrinterTurbo

Upstream license: MIT, copyright (c) 2024 Harry. See [UPSTREAM-LICENSE](UPSTREAM-LICENSE). This deployment wrapper is not affiliated with or endorsed by the upstream author.
