"""Playable title-linked video discovery."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class TrailerLibraryCard(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int = Field(gt=0)
    media_type: Literal["movie", "tv"]
    title: str
    release_year: int | None = None
    genre_ids: list[int] = Field(default_factory=list)
    poster_url: str | None = None
    youtube_key: str
    video_name: str
    video_type: Literal["Trailer", "Teaser", "Clip", "Featurette", "Behind the Scenes"]
    video_language: str | None = None
    official: bool = False
    future_path: str

class TrailerLibraryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(ge=1)
    has_more: bool = False
    items: list[TrailerLibraryCard] = Field(default_factory=list, max_length=24)
