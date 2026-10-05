"""Provider-neutral CineWatch catalog contracts for title, person and browse pages."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CatalogMediaType = Literal["movie", "tv"]


class CatalogRating(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["tmdb", "imdb", "rotten_tomatoes", "metacritic"]
    display_value: str = Field(min_length=1, max_length=40)


class CatalogNetwork(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int | None = Field(default=None, gt=0)
    kind: Literal["network", "company"] = "network"
    name: str = Field(min_length=1, max_length=160)
    logo_url: str | None = None


class CatalogWatchProvider(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=160)
    logo_url: str | None = None
    monetization_type: Literal["flatrate", "free", "ads", "rent", "buy"]


class CatalogTrailer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    youtube_key: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=240)
    video_type: Literal["Trailer", "Teaser", "Clip", "Featurette", "Behind the Scenes"]
    official: bool = False
    published_at: str | None = None
    season_number: int | None = Field(default=None, ge=0)


class CatalogVideosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: CatalogMediaType
    videos: list[CatalogTrailer] = Field(default_factory=list, max_length=20)


class CatalogCastMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=180)
    character: str | None = Field(default=None, max_length=240)
    profile_url: str | None = None
    future_path: str = Field(min_length=1, max_length=300)


class CatalogCrewMember(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=180)
    department: str | None = Field(default=None, max_length=120)
    job: str | None = Field(default=None, max_length=160)
    profile_url: str | None = None
    future_path: str = Field(min_length=1, max_length=300)


class CatalogReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_review_id: str = Field(min_length=1, max_length=160)
    author: str = Field(min_length=1, max_length=180)
    author_avatar_url: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=10.0)
    content: str = Field(min_length=1)
    created_at: str | None = None
    source: Literal["tmdb"] = "tmdb"
    source_label: Literal["TMDb"] = "TMDb"


class CatalogSeason(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int | None = Field(default=None, gt=0)
    season_number: int = Field(ge=0)
    name: str = Field(min_length=1, max_length=180)
    episode_count: int = Field(default=0, ge=0)
    air_date: str | None = None
    overview: str | None = None
    poster_url: str | None = None


class CatalogEpisode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    episode_number: int = Field(ge=0)
    season_number: int = Field(ge=0)
    name: str = Field(min_length=1, max_length=240)
    overview: str | None = None
    air_date: str | None = None
    runtime_minutes: int | None = Field(default=None, ge=0)
    still_url: str | None = None


class CatalogMediaSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: CatalogMediaType
    title: str = Field(min_length=1, max_length=260)
    year: int | None = Field(default=None, ge=1800, le=2200)
    poster_url: str | None = None
    backdrop_url: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=10.0)
    future_path: str = Field(min_length=1, max_length=300)


class CatalogTitleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: CatalogMediaType
    title: str = Field(min_length=1, max_length=260)
    original_title: str | None = Field(default=None, max_length=260)
    tagline: str | None = Field(default=None, max_length=600)
    overview: str | None = None
    release_date: str | None = None
    year: int | None = Field(default=None, ge=1800, le=2200)
    runtime_minutes: int | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, max_length=120)
    original_language: str | None = Field(default=None, max_length=20)
    genres: list[str] = Field(default_factory=list)
    poster_url: str | None = None
    backdrop_url: str | None = None
    ratings: list[CatalogRating] = Field(default_factory=list, max_length=4)
    networks: list[CatalogNetwork] = Field(default_factory=list, max_length=12)
    watch_region: str | None = Field(default=None, min_length=2, max_length=2)
    watch_providers: list[CatalogWatchProvider] = Field(default_factory=list, max_length=18)
    watch_information_url: str | None = None
    trailer: CatalogTrailer | None = None
    creators: list[str] = Field(default_factory=list, max_length=12)
    writers: list[str] = Field(default_factory=list, max_length=12)
    cast: list[CatalogCastMember] = Field(default_factory=list, max_length=18)
    crew: list[CatalogCrewMember] = Field(default_factory=list, max_length=30)
    seasons: list[CatalogSeason] = Field(default_factory=list, max_length=120)
    reviews: list[CatalogReview] = Field(default_factory=list, max_length=3)
    review_count: int = Field(default=0, ge=0)
    recommendations: list[CatalogMediaSummary] = Field(default_factory=list, max_length=12)
    awards: str | None = None
    box_office: str | None = None
    production_budget: int | None = Field(default=None, ge=0)
    revenue: int | None = Field(default=None, ge=0)


class CatalogReviewsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: CatalogMediaType
    page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    total_results: int = Field(ge=0)
    reviews: list[CatalogReview] = Field(default_factory=list, max_length=20)


class CatalogSeasonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    season_number: int = Field(ge=0)
    name: str = Field(min_length=1, max_length=180)
    overview: str | None = None
    poster_url: str | None = None
    episodes: list[CatalogEpisode] = Field(default_factory=list, max_length=100)


class CatalogPersonCredit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    media_type: CatalogMediaType
    title: str = Field(min_length=1, max_length=260)
    role: str | None = Field(default=None, max_length=240)
    year: int | None = Field(default=None, ge=1800, le=2200)
    popularity: float | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    future_path: str = Field(min_length=1, max_length=300)


class CatalogPersonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=220)
    biography: str | None = None
    known_for_department: str | None = Field(default=None, max_length=160)
    birthday: str | None = None
    deathday: str | None = None
    place_of_birth: str | None = Field(default=None, max_length=260)
    profile_url: str | None = None
    hero_backdrop_url: str | None = None
    credits: list[CatalogPersonCredit] = Field(default_factory=list, max_length=40)
    crew_credits: list[CatalogPersonCredit] = Field(default_factory=list, max_length=40)


class CatalogBrowseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["genre", "collection", "country"]
    slug: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=220)
    page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    total_results: int = Field(ge=0)
    media_type: Literal["all", "movie", "tv"]
    year: int | None = Field(default=None, ge=1800, le=2200)
    language: str | None = Field(default=None, max_length=20)
    genre: str | None = Field(default=None, max_length=120)
    sort: str = Field(min_length=1, max_length=80)
    items: list[CatalogMediaSummary] = Field(default_factory=list, max_length=24)


class CatalogProviderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=180)
    logo_url: str | None = None
    region: str = Field(min_length=2, max_length=2)
    official_homepage_url: str | None = None
    items: list[CatalogMediaSummary] = Field(default_factory=list, max_length=24)
