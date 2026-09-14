from __future__ import annotations

import asyncio

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.apify import ApifyScreenplayClient
from cinewatch_api.providers.kinocheck import KinoCheckClient
from cinewatch_api.providers.stands4 import Stands4LyricsClient
from cinewatch_api.providers.watchmode import WatchmodeClient


def test_watchmode_uses_header_not_query_secret() -> None:
    secret = "watchmode-test-secret"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == secret
        assert "apiKey" not in request.url.params
        return httpx.Response(200, json=[])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            payload = await WatchmodeClient(api_key=SecretStr(secret), http_client=client).get_json("/title/movie-278/sources/")
            assert payload == []

    asyncio.run(run())


def test_kinocheck_public_request_does_not_invent_api_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "X-Api-Key" not in request.headers
        assert request.url.path.endswith("/trailers/latest")
        return httpx.Response(200, json=[])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            payload = await KinoCheckClient(http_client=client).get_json("/trailers/latest")
            assert payload == []

    asyncio.run(run())



def test_kinocheck_keyed_request_sends_required_host_header() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Api-Key"] == "kino-test-secret"
        assert request.headers["X-Api-Host"] == "api.kinocheck.com"
        return httpx.Response(200, json=[])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            payload = await KinoCheckClient(api_key=SecretStr("kino-test-secret"), http_client=client).get_json("/trailers/latest")
            assert payload == []

    asyncio.run(run())

def test_stands4_lyrics_sends_term_and_artist_together() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["term"] == "Forever Young"
        assert request.url.params["artist"] == "Alphaville"
        assert request.url.params["format"] == "json"
        return httpx.Response(200, json={"result": []})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            payload = await Stands4LyricsClient(
                user_id=SecretStr("13777"), token=SecretStr("token"), http_client=client
            ).search("Forever Young", "Alphaville")
            assert payload == {"result": []}

    asyncio.run(run())


def test_apify_uses_official_actor_endpoint_and_bearer_token() -> None:
    secret = "apify-test-secret"

    def handler(request: httpx.Request) -> httpx.Response:
        assert "/v2/actors/thescrapelab~screenplay-script-scraper/run-sync-get-dataset-items" in str(request.url)
        assert request.headers["Authorization"] == f"Bearer {secret}"
        assert request.url.params["clean"] == "true"
        assert b'"movieName":"The Matrix"' in request.content
        return httpx.Response(200, json=[])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            payload = await ApifyScreenplayClient(token=SecretStr(secret), http_client=client).search_title("The Matrix")
            assert payload == []

    asyncio.run(run())
