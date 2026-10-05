"""People and organization discovery without browser-side provider credentials."""
from __future__ import annotations

from typing import Literal, cast
from fastapi import APIRouter, Path, Query, Request

from cinewatch_api.api.v1.media_authority import apply_media_authority
from cinewatch_api.catalog.directories import DirectoryService
from cinewatch_api.contracts.directories import OrganizationDetailResponse, OrganizationDirectoryResponse, PeopleDirectoryResponse
from cinewatch_api.errors import ApiError
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/directory", tags=["directory"])


def _service(request: Request) -> DirectoryService:
    settings = cast(Settings, request.app.state.settings)
    return DirectoryService(TmdbClient(api_key=settings.tmdb_api_key))


@router.get("/people", response_model=PeopleDirectoryResponse, operation_id="v1_directory_people")
async def people(request: Request, page: int = Query(default=1, ge=1, le=500), department: Literal["Acting", "Writing", "Directing", "Production"] | None = None) -> PeopleDirectoryResponse:
    try:
        payload = await _service(request).people(page, department)
        return apply_media_authority(request, "apply_people_directory", payload)
    except ProviderError as exc:
        raise ApiError(code="PEOPLE_UNAVAILABLE", message="People are temporarily unavailable.", status_code=503) from exc


@router.get("/organizations", response_model=OrganizationDirectoryResponse, operation_id="v1_directory_organizations")
async def organizations(request: Request, page: int = Query(default=1, ge=1, le=100)) -> OrganizationDirectoryResponse:
    try:
        payload = await _service(request).organizations(page)
        return apply_media_authority(request, "apply_organization_directory", payload)
    except ProviderError as exc:
        raise ApiError(code="ORGANIZATIONS_UNAVAILABLE", message="Organizations are temporarily unavailable.", status_code=503) from exc


@router.get("/{kind}/{provider_id}", response_model=OrganizationDetailResponse, operation_id="v1_directory_organization")
async def organization(request: Request, kind: Literal["network", "company"], provider_id: int = Path(gt=0)) -> OrganizationDetailResponse:
    try:
        payload = await _service(request).organization(kind, provider_id)
        return apply_media_authority(request, "apply_organization", payload)
    except ValueError as exc:
        raise ApiError(code="ORGANIZATION_NOT_FOUND", message="Organization not found.", status_code=404) from exc
    except ProviderError as exc:
        raise ApiError(code="ORGANIZATION_UNAVAILABLE", message="Organization is temporarily unavailable.", status_code=503) from exc
