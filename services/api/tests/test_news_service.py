from __future__ import annotations

import asyncio

from cinewatch_api.news.service import NewsService


class FakeNews:
    async def get_json(self, path: str, *, params=None):
        assert path == "/everything"
        assert params and params["q"] == "Lupita Nyong'o"
        return {
            "status": "ok",
            "totalResults": 2,
            "articles": [
                {
                    "source": {"name": "Example News"},
                    "author": "Reporter",
                    "title": "Lupita Nyong'o joins a new film",
                    "description": "A real normalized article shape.",
                    "url": "https://news.example/story",
                    "urlToImage": "https://news.example/image.jpg",
                    "publishedAt": "2026-09-12T10:00:00Z",
                },
                {
                    "source": {"name": "Unsafe Source"},
                    "title": "Unsafe URL is rejected",
                    "url": "http://news.example/unsafe",
                },
            ],
        }


def test_news_service_normalizes_and_rejects_non_https_articles() -> None:
    payload = asyncio.run(NewsService(FakeNews()).search("Lupita Nyong'o"))
    assert payload.total_results == 2
    assert len(payload.articles) == 1
    assert payload.articles[0].source.name == "Example News"
