"""Provider-neutral typed search contracts for CineWatch R3."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SearchEntityType = Literal["MOVIE", "TV_SHOW", "PERSON", "GENRE", "NETWORK_PROVIDER"]


class SearchSuggestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_type: SearchEntityType
    canonical_id: str = Field(min_length=1, max_length=200)
    provider_id: int | None = Field(default=None, gt=0)
    label: str = Field(min_length=1, max_length=300)
    secondary_text: str | None = Field(default=None, max_length=160)
    image_url: str | None = None
    destination: str = Field(min_length=1, max_length=360)
    source: Literal["tmdb", "cinewatch"]


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=100)
    suggestions: list[SearchSuggestion] = Field(default_factory=list, max_length=5)
