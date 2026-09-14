"""Experimental external-data qualification endpoints for the CineWatch test repo."""

from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Query, Request

from cinewatch_api.contracts.external import (
    ExternalAvailabilityResponse,
    ExternalTrailerLibraryResponse,
    LyricsLookupResponse,
    ScriptLookupResponse,
)
from cinewatch_api.errors import ApiError
from cinewatch_api.external.service import ExternalDataService
from cinewatch_api.providers.apify import ApifyScreenplayClient
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.kinocheck import KinoCheckClient
from cinewatch_api.providers.stands4 import Stands4LyricsClient
from cinewatch_api.providers.watchmode import WatchmodeClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/external", tags=["external-test"])


def _service(request: Request) -> ExternalDataService:
    settings = cast(Settings, request.app.state.settings)
    return ExternalDataService(
        watchmode=WatchmodeClient(api_key=settings.watchmode_api_key),
        kinocheck=KinoCheckClient(api_key=settings.kinocheck_api_key),
        lyrics=Stands4LyricsClient(
            user_id=settings.stands4_lyrics_user_id,
            token=settings.stands4_lyrics_token,
        ),
        screenplay=ApifyScreenplayClient(token=settings.apify_api_token),
    )


def _provider_failure(exc: ProviderError) -> ApiError:
    return ApiError(
        code="EXTERNAL_PROVIDER_UNAVAILABLE",
        message="The requested external data source is temporarily unavailable.",
        status_code=503,
    )


@router.get(
    "/where-to-watch",
    response_model=ExternalAvailabilityResponse,
    operation_id="v1_external_where_to_watch",
)
async def where_to_watch(
    request: Request,
    media_type: Literal["movie", "tv"] = Query(...),
    tmdb_id: int = Query(..., gt=0),
    region: str = Query(default="US", min_length=2, max_length=8),
) -> ExternalAvailabilityResponse:
    try:
        return await _service(request).where_to_watch(media_type, tmdb_id, region=region)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc
    except ValueError as exc:
        raise ApiError(code="EXTERNAL_QUERY_INVALID", message=str(exc), status_code=400) from exc


@router.get(
    "/trailers",
    response_model=ExternalTrailerLibraryResponse,
    operation_id="v1_external_trailers",
)
async def trailer_library(
    request: Request,
    page: int = Query(default=1, ge=1, le=1000),
    mode: Literal["latest", "trending"] = Query(default="latest"),
) -> ExternalTrailerLibraryResponse:
    try:
        return await _service(request).trailer_library(page=page, latest=mode == "latest")
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/lyrics",
    response_model=LyricsLookupResponse,
    operation_id="v1_external_lyrics",
)
async def lyrics_lookup(
    request: Request,
    term: str = Query(..., min_length=1, max_length=300),
    artist: str = Query(..., min_length=1, max_length=300),
    album: str | None = Query(default=None, min_length=1, max_length=300),
    reference_url: str | None = Query(default=None, max_length=1200),
) -> LyricsLookupResponse:
    try:
        return await _service(request).lyrics_lookup(term, artist, album=album, reference_url=reference_url)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc
    except ValueError as exc:
        raise ApiError(code="EXTERNAL_QUERY_INVALID", message=str(exc), status_code=400) from exc


@router.get(
    "/scripts",
    response_model=ScriptLookupResponse,
    operation_id="v1_external_scripts",
)
async def script_lookup(
    request: Request,
    title: str = Query(..., min_length=1, max_length=300),
    year: int | None = Query(default=None, ge=1800, le=2200),
) -> ScriptLookupResponse:
    try:
        return await _service(request).script_lookup(title, year=year)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc
    except ValueError as exc:
        raise ApiError(code="EXTERNAL_QUERY_INVALID", message=str(exc), status_code=400) from exc
