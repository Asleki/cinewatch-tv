"""Unversioned operational endpoints for probes and service inspection."""

from fastapi import APIRouter, Request

from cinewatch_api.api.system_state import health_response, status_response
from cinewatch_api.contracts.system import HealthResponse, StatusResponse

router = APIRouter(tags=["system"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service liveness",
    operation_id="system_health",
)
def health(request: Request) -> HealthResponse:
    return health_response(request)


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Service status",
    operation_id="system_status",
)
def status(request: Request) -> StatusResponse:
    return status_response(request)
