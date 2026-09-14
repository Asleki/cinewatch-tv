"""Normalize server-proxied NewsAPI results for CineWatch surfaces."""

from __future__ import annotations

from typing import Protocol
from urllib.parse import urlparse

from cinewatch_api.contracts.news import NewsArticle, NewsResponse, NewsSource


class NewsGateway(Protocol):
    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, str | int | bool] | None = None,
    ) -> dict[str, object]: ...


class NewsService:
    def __init__(self, news: NewsGateway) -> None:
        self._news = news

    async def search(self, query: str, *, page: int = 1, page_size: int = 12) -> NewsResponse:
        normalized = " ".join(query.split())
        if not normalized:
            raise ValueError("News query cannot be empty.")
        page = max(1, page)
        page_size = max(1, min(20, page_size))
        payload = await self._news.get_json(
            "/everything",
            params={
                "q": normalized,
                "language": "en",
                "sortBy": "publishedAt",
                "page": page,
                "pageSize": page_size,
            },
        )
        raw_articles = payload.get("articles")
        articles: list[NewsArticle] = []
        if isinstance(raw_articles, list):
            for raw in raw_articles:
                if not isinstance(raw, dict):
                    continue
                title = self._text(raw.get("title"))
                article_url = self._safe_https_url(raw.get("url"))
                if not title or not article_url:
                    continue
                source_raw = raw.get("source")
                source_name = (
                    self._text(source_raw.get("name"))
                    if isinstance(source_raw, dict)
                    else None
                ) or "News source"
                articles.append(
                    NewsArticle(
                        source=NewsSource(name=source_name),
                        author=self._text(raw.get("author")),
                        title=title,
                        description=self._text(raw.get("description")),
                        article_url=article_url,
                        image_url=self._safe_https_url(raw.get("urlToImage")),
                        published_at=self._text(raw.get("publishedAt")),
                    )
                )
                if len(articles) >= page_size:
                    break
        total = payload.get("totalResults")
        total_results = total if isinstance(total, int) and not isinstance(total, bool) else len(articles)
        return NewsResponse(
            query=normalized,
            page=page,
            page_size=page_size,
            total_results=max(0, total_results),
            articles=articles,
        )

    @staticmethod
    def _safe_https_url(value: object) -> str | None:
        text = NewsService._text(value)
        if not text:
            return None
        parsed = urlparse(text)
        if parsed.scheme != "https" or not parsed.netloc:
            return None
        return text

    @staticmethod
    def _text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        stripped = value.strip()
        return stripped or None
