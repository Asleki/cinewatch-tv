"""Runtime settings for the CineWatch TV API service."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "private-beta", "staging", "production"]
LogLevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Normalized backend settings loaded from environment variables or root .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: EnvironmentName = Field(default="local", validation_alias="CINEWATCH_ENV")
    app_name: str = Field(default="CineWatch TV", validation_alias="CINEWATCH_APP_NAME")
    service_name: str = Field(default="cinewatch-api", validation_alias="CINEWATCH_SERVICE_NAME")
    log_level: LogLevelName = Field(default="INFO", validation_alias="CINEWATCH_LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process settings singleton."""

    return Settings()
