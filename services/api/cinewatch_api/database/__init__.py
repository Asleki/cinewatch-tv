"""CineWatch PostgreSQL persistence foundation."""

from cinewatch_api.database.base import Base
from cinewatch_api.database.engine import create_database_engine
from cinewatch_api.database.session import create_session_factory
from cinewatch_api.database.url import (
    DatabaseConfigurationError,
    require_database_url,
    safe_database_url,
)

__all__ = [
    "Base",
    "DatabaseConfigurationError",
    "create_database_engine",
    "create_session_factory",
    "require_database_url",
    "safe_database_url",
]
