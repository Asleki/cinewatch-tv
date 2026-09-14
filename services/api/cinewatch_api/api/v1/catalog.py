"""CineWatch V1 catalog endpoints backing title, person, review and browse pages."""

from __future__ import annotations

from typing import Literal, cast

from fastapi import APIRouter, Path, Query, Request

from cinewatch_api.catalog import CatalogService
from cinewatch_api.contracts.catalog import (
    CatalogBrowseResponse,
    CatalogPersonResponse,
    CatalogReviewsResponse,
    CatalogSeasonResponse,
    CatalogTitleResponse,
)
from cinewatch_api.errors import ApiError
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.omdb import OmdbClient
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/catalog", tags=["catalog"])


def _service(request: Request) -> CatalogService:
    settings = cast(Settings, request.app.state.settings)
    return CatalogService(
        TmdbClient(api_key=settings.tmdb_api_key),
        OmdbClient(api_key=settings.omdb_api_key),
    )


def _provider_failure(exc: ProviderError) -> ApiError:
    return ApiError(
        code="CATALOG_PROVIDER_UNAVAILABLE",
        message="CineWatch catalog data is temporarily unavailable.",
        status_code=503,
    )


@router.get(
    "/title/{media_type}/{provider_id}",
    response_model=CatalogTitleResponse,
    summary="CineWatch title details",
    operation_id="v1_catalog_title",
)
async def catalog_title(
    request: Request,
    media_type: Literal["movie", "tv"],
    provider_id: int = Path(gt=0),
    region: str | None = Query(default=None, min_length=2, max_length=2),
) -> CatalogTitleResponse:
    try:
        return await _service(request).title(media_type, provider_id, watch_region=region)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/title/{media_type}/{provider_id}/reviews",
    response_model=CatalogReviewsResponse,
    summary="CineWatch title reviews",
    operation_id="v1_catalog_title_reviews",
)
async def catalog_reviews(
    request: Request,
    media_type: Literal["movie", "tv"],
    provider_id: int = Path(gt=0),
    page: int = Query(default=1, ge=1, le=1000),
) -> CatalogReviewsResponse:
    try:
        return await _service(request).reviews(media_type, provider_id, page=page)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/title/tv/{provider_id}/season/{season_number}",
    response_model=CatalogSeasonResponse,
    summary="CineWatch television season episodes",
    operation_id="v1_catalog_tv_season",
)
async def catalog_tv_season(
    request: Request,
    provider_id: int = Path(gt=0),
    season_number: int = Path(ge=0),
) -> CatalogSeasonResponse:
    try:
        return await _service(request).season(provider_id, season_number)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/person/{provider_id}",
    response_model=CatalogPersonResponse,
    summary="CineWatch person details",
    operation_id="v1_catalog_person",
)
async def catalog_person(
    request: Request,
    provider_id: int = Path(gt=0),
) -> CatalogPersonResponse:
    try:
        return await _service(request).person(provider_id)
    except ProviderError as exc:
        raise _provider_failure(exc) from exc


@router.get(
    "/browse/{kind}/{slug}",
    response_model=CatalogBrowseResponse,
    summary="Filtered CineWatch discovery browse",
    operation_id="v1_catalog_browse",
)
async def catalog_browse(
    request: Request,
    kind: Literal["genre", "collection", "country"],
    slug: str = Path(min_length=1, max_length=120),
    page: int = Query(default=1, ge=1, le=1000),
    media_type: Literal["all", "movie", "tv"] = Query(default="all"),
    year: int | None = Query(default=None, ge=1800, le=2200),
    language: str | None = Query(default=None, min_length=2, max_length=12),
    sort: str = Query(default="popularity.desc", pattern=r"^(popularity|vote_average|primary_release_date|first_air_date)\.(asc|desc)$"),
) -> CatalogBrowseResponse:
    try:
        return await _service(request).browse(
            kind,
            slug,
            page=page,
            media_type=media_type,
            year=year,
            language=language,
            sort=sort,
        )
    except ValueError as exc:
        raise ApiError(code="CATALOG_BROWSE_NOT_FOUND", message="This CineWatch discovery collection is unavailable.", status_code=404) from exc
    except ProviderError as exc:
        raise _provider_failure(exc) from exc
