"""Contracts for experimental external-data qualification surfaces in the test repo."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExternalAvailabilitySource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: int | None = Field(default=None, gt=0)
    name: str = Field(min_length=1, max_length=180)
    source_type: str | None = Field(default=None, max_length=80)
    region: str | None = Field(default=None, min_length=2, max_length=8)
    web_url: str | None = None
    format: str | None = Field(default=None, max_length=80)
    price: float | None = Field(default=None, ge=0)


class ExternalAvailabilityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    media_type: Literal["movie", "tv"]
    tmdb_id: int = Field(gt=0)
    region: str = Field(min_length=2, max_length=8)
    sources: list[ExternalAvailabilitySource] = Field(default_factory=list, max_length=200)


class ExternalTrailer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_id: str = Field(min_length=1, max_length=100)
    youtube_video_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=300)
    thumbnail_url: str | None = None
    language: str | None = Field(default=None, max_length=20)
    categories: list[str] = Field(default_factory=list, max_length=10)
    published_at: str | None = None
    media_type: Literal["movie", "tv"] | None = None
    tmdb_id: int | None = Field(default=None, gt=0)
    resource_title: str | None = Field(default=None, max_length=300)


class ExternalTrailerLibraryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    total_results: int = Field(ge=0)
    trailers: list[ExternalTrailer] = Field(default_factory=list, max_length=50)


class LyricsMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    song: str = Field(min_length=1, max_length=300)
    artist: str = Field(min_length=1, max_length=300)
    album: str | None = Field(default=None, max_length=300)
    song_url: str | None = None
    artist_url: str | None = None
    album_url: str | None = None


class LyricsLookupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    term: str = Field(min_length=1, max_length=300)
    artist: str = Field(min_length=1, max_length=300)
    album: str | None = Field(default=None, max_length=300)
    resolved: bool
    ambiguous: bool = False
    match: LyricsMatch | None = None
    candidates: list[LyricsMatch] = Field(default_factory=list, max_length=50)
    candidate_count: int = Field(default=0, ge=0)


class ScriptMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    year: int | None = Field(default=None, ge=1800, le=2200)
    source: str | None = Field(default=None, max_length=80)
    script_url: str | None = None
    download_url: str | None = None
    writers: list[str] = Field(default_factory=list, max_length=20)
    genres: list[str] = Field(default_factory=list, max_length=20)
    script_format: str | None = Field(default=None, max_length=40)
    has_script_text: bool = False
    word_count: int | None = Field(default=None, ge=0)
    scene_count: int | None = Field(default=None, ge=0)
    excerpt: str | None = Field(default=None, max_length=900)


class ScriptLookupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_title: str = Field(min_length=1, max_length=300)
    resolved: bool
    ambiguous: bool = False
    candidate_count: int = Field(default=0, ge=0)
    match: ScriptMatch | None = None


class ProviderQualificationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str = Field(min_length=1, max_length=80)
    status: Literal["PROVEN", "PARTIAL", "FAILED", "NOT_AUTHORIZED", "EVALUATION_ONLY", "CONFIGURED"]
    detail: str = Field(min_length=1, max_length=500)


class ProviderQualificationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ProviderQualificationItem] = Field(default_factory=list, max_length=30)
