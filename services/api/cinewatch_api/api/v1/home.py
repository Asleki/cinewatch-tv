"""CineWatch V1 homepage endpoint."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request

from cinewatch_api.contracts.home import HomeResponse
from cinewatch_api.errors import ApiError
from cinewatch_api.home.aggregation import HomepageAggregator
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.settings import Settings

router = APIRouter(tags=["home"])


@router.get(
    "/home",
    response_model=HomeResponse,
    summary="CineWatch V1 homepage",
    operation_id="v1_home",
)
async def home(request: Request) -> HomeResponse:
    """Return a provider-neutral homepage assembled from TMDb."""

    settings = cast(Settings, request.app.state.settings)
    aggregator = HomepageAggregator(
        TmdbClient(api_key=settings.tmdb_api_key),
    )
    try:
        return await aggregator.build()
    except ProviderError as exc:
        raise ApiError(
            code="HOMEPAGE_DATA_UNAVAILABLE",
            message="Homepage data is temporarily unavailable.",
            status_code=503,
        ) from exc
