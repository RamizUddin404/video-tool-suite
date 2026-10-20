from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    app_api_key: str = ""
    openrouter_video_model: str = "google/veo-3.1"
    allowed_origins: str = "https://ramizuddin404.github.io,http://localhost:8000,http://127.0.0.1:8000"
    request_timeout_seconds: int = 1800
    output_dir: str = "/tmp/linktoon-outputs"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def outputs_path(self) -> Path:
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
