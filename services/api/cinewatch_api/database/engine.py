"""SQLAlchemy engine construction for the CineWatch PostgreSQL authority."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine

from cinewatch_api.database.url import require_database_url
from cinewatch_api.settings import Settings


def create_database_engine(settings: Settings | None = None) -> Engine:
    """Create a lazy PostgreSQL engine; no connection is opened by this function."""

    return create_engine(
        require_database_url(settings),
        pool_pre_ping=True,
    )
