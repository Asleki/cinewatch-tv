"""Shared constructors for operational endpoint payloads."""

from fastapi import Request

from cinewatch_api.contracts.system import HealthResponse, StatusResponse
from cinewatch_api.settings import Settings


def _settings(request: Request) -> Settings:
    settings = getattr(request.app.state, "settings", None)
    if not isinstance(settings, Settings):
        raise RuntimeError("CineWatch API settings are not initialized.")
    return settings


def health_response(request: Request) -> HealthResponse:
    settings = _settings(request)
    return HealthResponse(service=settings.service_name)


def status_response(request: Request) -> StatusResponse:
    settings = _settings(request)
    return StatusResponse(
        service=settings.service_name,
        application=settings.app_name,
        environment=settings.environment,
    )
