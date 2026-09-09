"""FastAPI application factory."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cinewatch_api import __version__
from cinewatch_api.api.system import router as system_router
from cinewatch_api.api.v1.router import router as v1_router
from cinewatch_api.constants import API_V1_PREFIX
from cinewatch_api.errors import register_exception_handlers
from cinewatch_api.logging import configure_logging
from cinewatch_api.middleware.request_id import RequestIdMiddleware
from cinewatch_api.settings import Settings, get_settings

logger = logging.getLogger("cinewatch.api")


def _lifespan(settings: Settings) -> Callable[[FastAPI], AsyncIterator[None]]:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = settings
        logger.info(
            "CineWatch API started",
            extra={
                "event": "service.started",
                "service": settings.service_name,
                "environment": settings.environment,
            },
        )
        yield
        logger.info(
            "CineWatch API stopped",
            extra={
                "event": "service.stopped",
                "service": settings.service_name,
                "environment": settings.environment,
            },
        )

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create a fully configured CineWatch backend application."""

    runtime_settings = settings or get_settings()
    configure_logging(runtime_settings.log_level)

    app = FastAPI(
        title="CineWatch TV API",
        version=__version__,
        description="CineWatch TV V1 backend service boundary.",
        openapi_version="3.1.0",
        lifespan=_lifespan(runtime_settings),
    )
    app.state.settings = runtime_settings
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(system_router)
    app.include_router(v1_router, prefix=API_V1_PREFIX)
    return app
