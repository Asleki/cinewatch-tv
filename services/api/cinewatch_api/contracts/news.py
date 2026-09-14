"""Normalized NewsAPI contracts for CineWatch R3."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class NewsSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)


class NewsArticle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: NewsSource
    author: str | None = Field(default=None, max_length=300)
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    article_url: str
    image_url: str | None = None
    published_at: str | None = None


class NewsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=200)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=20)
    total_results: int = Field(ge=0)
    articles: list[NewsArticle] = Field(default_factory=list, max_length=20)
