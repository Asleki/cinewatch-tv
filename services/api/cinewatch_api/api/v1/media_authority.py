"""Fail-open optional PostgreSQL media authority application."""

from __future__ import annotations

import logging
from typing import Any, cast

from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from cinewatch_api.database.engine import create_database_engine
from cinewatch_api.database.session import create_session_factory
from cinewatch_api.media.authority import MediaAuthority
from cinewatch_api.settings import Settings

logger = logging.getLogger("cinewatch.media")


def apply_media_authority(request: Request, method: str, payload: Any) -> Any:
    """Apply approved overrides/log gaps when DB exists; never hide provider content on DB failure."""

    settings = cast(Settings, request.app.state.settings)
    if settings.database_url is None or not settings.database_url.get_secret_value().strip():
        return payload
    try:
        factory = getattr(request.app.state, "media_session_factory", None)
        if factory is None:
            engine = create_database_engine(settings)
            factory = create_session_factory(engine)
            request.app.state.media_session_factory = factory
        with factory() as session:
            authority = MediaAuthority(session)
            return getattr(authority, method)(payload)
    except (SQLAlchemyError, OSError, RuntimeError, AttributeError) as exc:
        logger.warning(
            "CineWatch media authority unavailable; provider content remains eligible",
            extra={"event": "media.authority.fail_open", "error_type": type(exc).__name__},
        )
        return payload
