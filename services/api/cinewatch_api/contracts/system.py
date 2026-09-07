"""System endpoint response contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from cinewatch_api.settings import EnvironmentName


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"] = "ok"
    service: str


class StatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ready"] = "ready"
    service: str
    application: str
    environment: EnvironmentName
    api_version: Literal["v1"] = "v1"
