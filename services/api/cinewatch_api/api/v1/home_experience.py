"""Interactive CineWatch V1 homepage experience endpoints."""

from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Path, Query, Request

from cinewatch_api.contracts.home_experience import (
    HomeGenresResponse,
    HomeHeroExperience,
    HomeRailResponse,
    HomeSearchResponse,
    HomeTrailerRailResponse,
)
from cinewatch_api.errors import ApiError
from cinewatch_api.home.experience import HomepageExperienceService, RAIL_TITLES
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.omdb import OmdbClient
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/home", tags=["home"])


def _service(request: Request) -> HomepageExperienceService:
    settings = cast(Settings, request.app.state.settings)
    return HomepageExperienceService(
        TmdbClient(api_key=settings.tmdb_api_key),
        OmdbClient(api_key=settings.omdb_api_key),
    )


def _provider_failure(exc: ProviderError) -> ApiError:
    return ApiError(
        code="HOMEPAGE_EXPERIENCE_UNAVAILABLE",
        message="Homepage discovery is temporarily unavailable.",
        status_code=503,
    )


@router.get(
    "/rails/{slug}",
    response_model=HomeRailResponse,
    summary="Lazy CineWatch homepage rail",
    operation_id="v1_home_rail",
)
async def home_rail(
    request: Request,
    slug: str = Path(min_length=1, max_length=80),
) -> HomeRailResponse:
    if slug not in RAIL_TITLES:
        raise ApiError(
            code="HOMEPAGE_RAIL_NOT_FOUND",
            message="Homepage rail is not available.",
            status_code=404,
        )
    try:
        return await _service(request).rail(slug)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/trailers",
    response_model=HomeTrailerRailResponse,
    summary="Lazy CineWatch homepage trailer rail",
    operation_id="v1_home_trailers",
)
async def home_trailers(request: Request) -> HomeTrailerRailResponse:
    try:
        return await _service(request).trailer_rail()
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/search",
    response_model=HomeSearchResponse,
    summary="CineWatch homepage search suggestions",
    operation_id="v1_home_search",
)
async def home_search(
    request: Request,
    q: str = Query(min_length=2, max_length=100),
) -> HomeSearchResponse:
    try:
        return await _service(request).search(q)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/genres",
    response_model=HomeGenresResponse,
    summary="Dynamic CineWatch homepage genres",
    operation_id="v1_home_genres",
)
async def home_genres(request: Request) -> HomeGenresResponse:
    try:
        return await _service(request).genres()
    except ProviderError as exc:
        raise _provider_failure(exc) from exc




@router.get(
    "/hero/{media_type}/{provider_id}",
    response_model=HomeHeroExperience,
    summary="Lazy CineWatch homepage hero enrichment",
    operation_id="v1_home_hero_experience",
)
async def home_hero_experience(
    request: Request,
    media_type: Literal["movie", "tv"],
    provider_id: int = Path(gt=0),
) -> HomeHeroExperience:
    try:
        return await _service(request).hero(media_type, provider_id)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc
