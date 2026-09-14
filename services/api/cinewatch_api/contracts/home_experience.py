"""Public contracts for the interactive CineWatch homepage experience."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from cinewatch_api.contracts.home import HomeItem

ExperienceMediaType = Literal["movie", "tv", "person"]


class HomeExternalRating(BaseModel):
    """One secondary rating shown only when an upstream actually supplies it."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["imdb", "rotten_tomatoes", "metacritic"]
    display_value: str = Field(min_length=1, max_length=32)


class HomeTrailer(BaseModel):
    """One deterministically selected YouTube trailer or teaser."""

    model_config = ConfigDict(extra="forbid")

    youtube_key: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=300)
    video_type: Literal["Trailer", "Teaser"]
    official: bool = False
    published_at: str | None = None
    season_number: int | None = Field(default=None, ge=0)


class HomeHeroExperience(BaseModel):
    """Lazy, high-value enrichment for the single homepage hero."""

    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: Literal["movie", "tv"]
    writers: list[str] = Field(default_factory=list, max_length=5)
    ratings: list[HomeExternalRating] = Field(default_factory=list, max_length=3)
    trailer: HomeTrailer | None = None
    quote: str | None = None


class HomeRailResponse(BaseModel):
    """One bounded lazy homepage discovery rail."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=100)
    items: list[HomeItem] = Field(default_factory=list, max_length=12)


class HomeTrailerCard(BaseModel):
    """A homepage trailer card that is guaranteed to have a playable trailer."""

    model_config = ConfigDict(extra="forbid")

    item: HomeItem
    trailer: HomeTrailer


class HomeTrailerRailResponse(BaseModel):
    """Bounded trailer rail loaded only when its homepage region becomes relevant."""

    model_config = ConfigDict(extra="forbid")

    slug: Literal["teasers-trailers"] = "teasers-trailers"
    title: Literal["Teasers & Trailers"] = "Teasers & Trailers"
    items: list[HomeTrailerCard] = Field(default_factory=list, max_length=6)


class HomeSearchSuggestion(BaseModel):
    """Lightweight suggestion carrying identity for a future route without navigating now."""

    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: ExperienceMediaType
    label: str = Field(min_length=1, max_length=300)
    secondary_text: str | None = Field(default=None, max_length=120)
    image_url: str | None = None
    future_path: str = Field(min_length=1, max_length=300)


class HomeSearchResponse(BaseModel):
    """Bounded homepage search suggestions from CineWatch's provider boundary."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=100)
    suggestions: list[HomeSearchSuggestion] = Field(default_factory=list, max_length=8)


class HomeGenreEntry(BaseModel):
    """Merged dynamic TMDb genre identity for homepage discovery."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    movie_provider_id: int | None = Field(default=None, gt=0)
    tv_provider_id: int | None = Field(default=None, gt=0)
    future_path: str = Field(min_length=1, max_length=300)


class HomeGenresResponse(BaseModel):
    """Dynamic movie and television genres used by homepage discovery and search."""

    model_config = ConfigDict(extra="forbid")

    genres: list[HomeGenreEntry] = Field(default_factory=list)
