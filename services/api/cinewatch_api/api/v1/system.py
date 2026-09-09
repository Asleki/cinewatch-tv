"""Versioned system contract used to prove the V1 namespace."""

from fastapi import APIRouter, Request

from cinewatch_api.api.system_state import status_response
from cinewatch_api.contracts.system import StatusResponse

router = APIRouter(tags=["system"])


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="V1 API status",
    operation_id="v1_system_status",
)
def status(request: Request) -> StatusResponse:
    return status_response(request)
