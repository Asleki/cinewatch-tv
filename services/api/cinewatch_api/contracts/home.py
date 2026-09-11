"""Public CineWatch V1 homepage response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

HomeMediaType = Literal["movie", "tv", "person"]
HomeRemediation = Literal["AWAITING_HUMAN_RESEARCH", "GENERATION_ALLOWED"]


class HomeRating(BaseModel):
    """Normalized rating metadata retained from the primary provider."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["tmdb"] = "tmdb"
    value: float = Field(ge=0.0, le=10.0)
    count: int = Field(ge=0)
    scale: Literal[10] = 10


class HomeMediaGap(BaseModel):
    """Stable missing-media instruction emitted by CineWatch."""

    model_config = ConfigDict(extra="forbid")

    provider: Literal["tmdb"] = "tmdb"
    entity_type: Literal["person", "network", "movie", "tv"]
    provider_id: int = Field(gt=0)
    entity_name: str = Field(min_length=1)
    asset_kind: Literal["profile", "logo", "poster", "backdrop"]
    remediation: HomeRemediation
    suggested_filename: str = Field(min_length=1)
    public_path: str = Field(min_length=1)


class HomeItem(BaseModel):
    """Provider-neutral item consumed by CineWatch homepage clients."""

    model_config = ConfigDict(extra="forbid")

    provider: Literal["tmdb"] = "tmdb"
    provider_id: int = Field(gt=0)
    media_type: HomeMediaType
    title: str = Field(min_length=1)
    overview: str | None = None
    date: str | None = None
    popularity: float | None = None
    rating: HomeRating | None = None
    poster_url: str | None = None
    backdrop_url: str | None = None
    profile_url: str | None = None
    known_for_department: str | None = None
    media_gaps: list[HomeMediaGap] = Field(default_factory=list)


class HomeSections(BaseModel):
    """Bounded homepage rails owned by the CineWatch API."""

    model_config = ConfigDict(extra="forbid")

    trending: list[HomeItem] = Field(default_factory=list)
    popular_movies: list[HomeItem] = Field(default_factory=list)
    popular_tv: list[HomeItem] = Field(default_factory=list)
    trending_people: list[HomeItem] = Field(default_factory=list)


class HomeResponse(BaseModel):
    """Canonical V1 homepage payload."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    primary_provider: Literal["tmdb"] = "tmdb"
    hero: HomeItem | None = None
    sections: HomeSections
