import pytest
from pydantic import SecretStr

from cinewatch_api.database.url import (
    DatabaseConfigurationError,
    require_database_url,
    safe_database_url,
)
from cinewatch_api.settings import Settings


def test_database_url_is_optional_until_database_operation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)

    assert settings.database_url is None
    with pytest.raises(DatabaseConfigurationError, match="not configured"):
        require_database_url(settings)


def test_database_url_accepts_only_psycopg_postgresql() -> None:
    settings = Settings(
        database_url=SecretStr(
            "postgresql+psycopg://cinewatch_app:secret@localhost:5432/cinewatch_dev"
        ),
        _env_file=None,
    )

    url = require_database_url(settings)

    assert url.drivername == "postgresql+psycopg"
    assert url.database == "cinewatch_dev"


def test_database_url_rejects_non_postgresql_driver() -> None:
    settings = Settings(
        database_url=SecretStr("sqlite:///cinewatch.db"),
        _env_file=None,
    )

    with pytest.raises(DatabaseConfigurationError, match="postgresql\\+psycopg"):
        require_database_url(settings)


def test_database_url_redacts_password() -> None:
    settings = Settings(
        database_url=SecretStr(
            "postgresql+psycopg://cinewatch_app:super-secret@localhost:5432/cinewatch_dev"
        ),
        _env_file=None,
    )

    rendered = safe_database_url(require_database_url(settings))

    assert "super-secret" not in rendered
    assert "***" in rendered
    assert "cinewatch_dev" in rendered
