from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    replicate_api_token: str = ""
    replicate_model_version: str = ""
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    provider_poll_seconds: float = 3.0
    job_timeout_seconds: int = 1800
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

settings = Settings()
