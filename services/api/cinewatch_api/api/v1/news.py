"""Live CineWatch news endpoint backed by NewsAPI."""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Query, Request

from cinewatch_api.contracts.news import NewsResponse
from cinewatch_api.errors import ApiError
from cinewatch_api.news import NewsService
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.newsapi import NewsApiClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/news", tags=["news"])


def _service(request: Request) -> NewsService:
    settings = cast(Settings, request.app.state.settings)
    return NewsService(NewsApiClient(api_key=settings.news_api_key))


@router.get(
    "",
    response_model=NewsResponse,
    summary="Live CineWatch entertainment news",
    operation_id="v1_news",
)
async def news(
    request: Request,
    q: str = Query(default="film OR television", min_length=1, max_length=200),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=20),
) -> NewsResponse:
    try:
        return await _service(request).search(q, page=page, page_size=page_size)
    except ProviderError as exc:
        raise ApiError(
            code="NEWS_PROVIDER_UNAVAILABLE",
            message="CineWatch News is temporarily unavailable.",
            status_code=503,
        ) from exc
