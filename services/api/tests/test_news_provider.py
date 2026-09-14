from __future__ import annotations

import asyncio

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.newsapi import NewsApiClient


def test_newsapi_client_uses_server_header_and_parses_payload() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["x-api-key"] == "secret-news-key"
            assert request.url.params["q"] == "film"
            return httpx.Response(200, json={"status": "ok", "totalResults": 0, "articles": []})

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            payload = await NewsApiClient(
                api_key=SecretStr("secret-news-key"),
                http_client=http_client,
            ).get_json("/everything", params={"q": "film"})
        assert payload["status"] == "ok"

    asyncio.run(run())
