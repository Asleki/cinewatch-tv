"""NexVox Voice Lab contracts for consent-governed training capture."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VoiceSampleMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tester_id: Literal["tester-01", "tester-02", "tester-03", "tester-04"]
    session_id: str = Field(min_length=8, max_length=120)
    recorded_at: str = Field(min_length=10, max_length=80)
    language: str = Field(min_length=2, max_length=40)
    prompt: str = Field(min_length=1, max_length=500)
    sample_rate: int = Field(ge=8000, le=192000)
    duration_seconds: float = Field(gt=0.0, le=300.0)
    consent_version: Literal["CWTV-NEXVOX-CONSENT-R3-001"]


class VoiceSampleStageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: VoiceSampleMetadata
    wav_base64: str = Field(min_length=16, max_length=20_000_000)


class VoiceSampleStageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: str = Field(min_length=12, max_length=120)
    stored: bool
    retention_status: Literal["LOCAL_PRIVATE_STAGING"] = "LOCAL_PRIVATE_STAGING"
