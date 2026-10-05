"""Playable trailer directory."""
from __future__ import annotations
from typing import Literal, cast
from fastapi import APIRouter, Query, Request
from cinewatch_api.catalog.trailer_library import MAX_TRAILER_PAGE, TrailerLibraryService
from cinewatch_api.contracts.trailer_library import TrailerLibraryResponse
from cinewatch_api.errors import ApiError
from cinewatch_api.providers.errors import ProviderError
from cinewatch_api.providers.tmdb import TmdbClient
from cinewatch_api.settings import Settings

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("/trailers", response_model=TrailerLibraryResponse, operation_id="v1_catalog_trailer_library")
async def trailer_library(request: Request, page: int = Query(default=1, ge=1, le=MAX_TRAILER_PAGE), media_type: Literal["all", "movie", "tv"] = "all", genre: str | None = Query(default=None, max_length=120), year: int | None = Query(default=None, ge=1880, le=2200), video_language: str | None = Query(default=None, min_length=2, max_length=2), video_type: Literal["Trailer", "Teaser", "Clip", "Featurette", "Behind the Scenes"] | None = None) -> TrailerLibraryResponse:
    settings = cast(Settings, request.app.state.settings)
    try:
        return await TrailerLibraryService(TmdbClient(api_key=settings.tmdb_api_key)).browse(page=page, media_type=media_type, genre=genre, year=year, video_language=video_language, video_type=video_type)
    except ProviderError as exc:
        raise ApiError(code="TRAILERS_UNAVAILABLE", message="Trailers are temporarily unavailable.", status_code=503) from exc
