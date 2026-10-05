"""Bounded, source-labelled discovery directories."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class PersonDirectoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int = Field(gt=0)
    name: str
    profile_url: str | None = None
    known_for_department: str | None = None
    future_path: str


class PeopleDirectoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    department: str | None = None
    items: list[PersonDirectoryItem] = Field(default_factory=list, max_length=20)


class OrganizationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: int = Field(gt=0)
    kind: Literal["network", "company"]
    name: str
    logo_url: str | None = None
    origin_country: str | None = None
    headquarters: str | None = None
    homepage_url: str | None = None
    future_path: str


class OrganizationDirectoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page: int = Field(ge=1)
    has_more: bool = False
    items: list[OrganizationItem] = Field(default_factory=list, max_length=100)


class OrganizationDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    organization: OrganizationItem
    description: str | None = None
    backdrop_url: str | None = None
    backdrop_media_type: Literal["movie", "tv"] | None = None
    backdrop_title_id: int | None = None
    backdrop_title_name: str | None = None
    movie_count: int | None = None
    series_count: int | None = None
