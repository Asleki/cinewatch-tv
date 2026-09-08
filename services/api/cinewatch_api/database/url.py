"""Database URL validation and redaction."""

from __future__ import annotations

from sqlalchemy.engine import URL, make_url

from cinewatch_api.settings import Settings, get_settings

POSTGRESQL_DRIVER = "postgresql+psycopg"


class DatabaseConfigurationError(RuntimeError):
    """Raised when the CineWatch PostgreSQL configuration is absent or invalid."""


def require_database_url(settings: Settings | None = None) -> URL:
    """Return the validated CineWatch PostgreSQL URL without opening a connection."""

    runtime_settings = settings or get_settings()
    if runtime_settings.database_url is None:
        raise DatabaseConfigurationError("DATABASE_URL is not configured")

    raw_url = runtime_settings.database_url.get_secret_value().strip()
    if not raw_url:
        raise DatabaseConfigurationError("DATABASE_URL is not configured")

    try:
        url = make_url(raw_url)
    except Exception as exc:  # SQLAlchemy raises several URL parsing exceptions.
        raise DatabaseConfigurationError("DATABASE_URL is invalid") from exc

    if url.drivername != POSTGRESQL_DRIVER:
        raise DatabaseConfigurationError(
            f"DATABASE_URL must use the {POSTGRESQL_DRIVER} driver"
        )
    if not url.database:
        raise DatabaseConfigurationError("DATABASE_URL must name a CineWatch database")

    return url


def safe_database_url(url: URL) -> str:
    """Render a database URL with credentials redacted for diagnostics."""

    return url.render_as_string(hide_password=True)
