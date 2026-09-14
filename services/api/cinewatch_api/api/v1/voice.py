"""NexVox Voice Lab V1 staging endpoint."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request

from cinewatch_api.contracts.voice import VoiceSampleStageRequest, VoiceSampleStageResponse
from cinewatch_api.errors import ApiError
from cinewatch_api.settings import Settings
from cinewatch_api.voice.service import InvalidVoiceSampleError, VoiceStagingDisabledError, VoiceStagingService

router = APIRouter(prefix="/voice-lab", tags=["voice-lab"])


@router.post(
    "/samples",
    response_model=VoiceSampleStageResponse,
    summary="Stage an explicitly accepted NexVox WAV sample",
    operation_id="v1_voice_stage_sample",
)
async def stage_voice_sample(request: Request, payload: VoiceSampleStageRequest) -> VoiceSampleStageResponse:
    settings = cast(Settings, request.app.state.settings)
    service = VoiceStagingService(settings.nexvox_voice_staging_dir)
    try:
        return service.stage(payload)
    except VoiceStagingDisabledError as exc:
        raise ApiError(
            code="NEXVOX_STAGING_NOT_CONFIGURED",
            message="NexVox secure staging is not configured in this runtime.",
            status_code=503,
        ) from exc
    except InvalidVoiceSampleError as exc:
        raise ApiError(code="NEXVOX_SAMPLE_INVALID", message=str(exc), status_code=422) from exc
