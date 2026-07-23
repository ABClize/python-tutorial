"""Application configuration with pydantic-settings."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings with explicit validation.

    Interview points:
    - Secrets should not be hard-coded in a production repository.
    - Settings are parsed once at the application boundary.
    - ``SecretStr`` masks values in logs and ``repr`` but is not encryption.
    """

    model_config = SettingsConfigDict(
        env_prefix="INTERVIEW_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Backend Interview Lab"
    environment: str = "development"
    api_key: SecretStr = SecretStr("development-only-key")
    request_timeout_seconds: float = Field(default=0.25, gt=0, le=30)
    max_concurrency: int = Field(default=4, ge=1, le=100)


@lru_cache
def get_settings() -> Settings:
    """Create settings once per process; tests can clear or override this dependency."""
    return Settings()
