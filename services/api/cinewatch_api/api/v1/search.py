"""Typed CineWatch entity search endpoint."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Query, Request

from cinewatch_api.contracts.search import SearchResponse
from cinewatch_api.api.v1.media_authority import apply_media_authority
from cinewatch_api.errors import ApiError
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.search import SearchService
from cinewatch_api.settings import Settings

router = APIRouter(tags=["search"])


def _service(request: Request) -> SearchService:
    settings = cast(Settings, request.app.state.settings)
    return SearchService(TmdbClient(api_key=settings.tmdb_api_key))


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Typed CineWatch entity search",
    operation_id="v1_search",
)
async def search(
    request: Request,
    q: str = Query(min_length=2, max_length=100),
) -> SearchResponse:
    try:
        payload = await _service(request).search(q)
        return apply_media_authority(request, "apply_search", payload)
    except ProviderError as exc:
        raise ApiError(
            code="SEARCH_PROVIDER_UNAVAILABLE",
            message="CineWatch search is temporarily unavailable.",
            status_code=503,
        ) from exc
