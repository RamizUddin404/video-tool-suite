# LinkToon Studio

LinkToon is a static GitHub Pages site. Creator Studio now calls the **OpenRouter video API directly**; it does not require a Hugging Face Space or a separate backend for the direct-generation flow.

- Website: https://ramizuddin404.github.io/video-tool-suite/
- Creator Studio: https://ramizuddin404.github.io/video-tool-suite/editor.html
- OpenRouter video API documentation: https://openrouter.ai/docs/api/api-reference/video-generation/create-videos

## Use Creator Studio

1. Open Creator Studio.
2. Enter an OpenRouter API key you are authorized to use.
3. Confirm the video model ID is available to your account (the default is `google/veo-3.1`).
4. Enter a topic/story prompt and choose your creative preferences.
5. Submit the job, then use **Refresh status** while OpenRouter generates the clip.

Video generation is asynchronous: OpenRouter returns a job ID first, then the page polls for completion and presents the output when available.

## Important security and capability notes

- The direct browser flow sends the API key from your browser to OpenRouter. The page does not save it, but browser-based keys are **not suitable for a public production app**: anyone who can modify or inspect the served JavaScript or browser session may expose the key. Use a key with appropriate limits, do not use a shared device, and revoke it if you believe it was exposed.
- If the browser blocks direct requests with a CORS error, a server-side proxy is required. OpenRouter can remain the only AI provider, but a proxy would still be needed to protect credentials and relay requests.
- A URL entered in the prompt is not automatically watched or transcribed. For a video-based adaptation, provide a written summary or transcript in the topic field.
- Duration and aspect-ratio choices are prompt guidance in this starter UI, not guaranteed API parameters. Model capabilities vary; check the current OpenRouter video model documentation before relying on a specific duration, ratio, resolution, or audio feature.
- Video generation may incur charges on the OpenRouter account. Check pricing and account limits before submitting a job.
- The older FastAPI backend files remain in the repository for reference, but the Creator Studio's current direct flow does not call them.

## Repository

https://github.com/RamizUddin404/video-tool-suite
