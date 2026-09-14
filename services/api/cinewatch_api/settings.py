"""Runtime settings for the CineWatch TV API service."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "private-beta", "staging", "production"]
LogLevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Normalized backend settings loaded from environment variables or root .env."""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: EnvironmentName = Field(default="local", validation_alias="CINEWATCH_ENV")
    app_name: str = Field(default="CineWatch TV", validation_alias="CINEWATCH_APP_NAME")
    service_name: str = Field(default="cinewatch-api", validation_alias="CINEWATCH_SERVICE_NAME")
    log_level: LogLevelName = Field(default="INFO", validation_alias="CINEWATCH_LOG_LEVEL")
    database_url: SecretStr | None = Field(default=None, validation_alias="DATABASE_URL")
    tmdb_api_key: SecretStr | None = Field(default=None, validation_alias="TMDB_API_KEY")
    omdb_api_key: SecretStr | None = Field(default=None, validation_alias="OMDB_API_KEY")
    news_api_key: SecretStr | None = Field(default=None, validation_alias="NEWS_API_KEY")
    watchmode_api_key: SecretStr | None = Field(default=None, validation_alias="WATCHMODE_API_KEY")
    kinocheck_api_key: SecretStr | None = Field(default=None, validation_alias="KINOCHECK_API_KEY")
    apify_api_token: SecretStr | None = Field(default=None, validation_alias="APIFY_API_TOKEN")
    stands4_lyrics_user_id: SecretStr | None = Field(default=None, validation_alias="STANDS4_LYRICS_USER_ID")
    stands4_lyrics_token: SecretStr | None = Field(default=None, validation_alias="STANDS4_LYRICS_TOKEN")
    stands4_user_id_1: SecretStr | None = Field(default=None, validation_alias="STANDS4_USER_ID_1")
    stands4_token_1: SecretStr | None = Field(default=None, validation_alias="STANDS4_TOKEN_1")
    stands4_user_id_2: SecretStr | None = Field(default=None, validation_alias="STANDS4_USER_ID_2")
    stands4_token_2: SecretStr | None = Field(default=None, validation_alias="STANDS4_TOKEN_2")
    nexvox_voice_staging_dir: str | None = Field(default=None, validation_alias="NEXVOX_VOICE_STAGING_DIR")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process settings singleton."""

    return Settings()
