from __future__ import annotations

import asyncio

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
)
from cinewatch_api.providers.omdb import OmdbClient
from cinewatch_api.providers.tmdb import TmdbClient


def test_tmdb_client_authenticates_server_side() -> None:
    secret = "tmdb-test-secret"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["api_key"] == secret
        return httpx.Response(
            200, json={"images": {"secure_base_url": "https://image.tmdb.org/t/p/"}}
        )

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            payload = await TmdbClient(
                api_key=SecretStr(secret), http_client=http_client
            ).configuration()
            assert isinstance(payload["images"], dict)

    asyncio.run(run())


def test_tmdb_client_normalizes_rate_limit_without_leaking_secret() -> None:
    secret = "tmdb-rate-limit-secret"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"status_message": "Too many requests"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            try:
                await TmdbClient(
                    api_key=SecretStr(secret), http_client=http_client
                ).configuration()
            except ProviderRateLimitError as exc:
                assert exc.code == "TMDB_RATE_LIMITED"
                assert secret not in str(exc)
            else:
                raise AssertionError("expected ProviderRateLimitError")

    asyncio.run(run())


def test_omdb_client_enriches_by_imdb_identity() -> None:
    secret = "omdb-test-secret"
    imdb_id = "tt0111161"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["apikey"] == secret
        assert request.url.params["i"] == imdb_id
        return httpx.Response(200, json={"Response": "True", "imdbID": imdb_id, "Ratings": []})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            payload = await OmdbClient(
                api_key=SecretStr(secret), http_client=http_client
            ).lookup_imdb(imdb_id)
            assert payload["imdbID"] == imdb_id

    asyncio.run(run())


def test_omdb_client_normalizes_invalid_api_key() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"Response": "False", "Error": "Invalid API key!"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
            try:
                await OmdbClient(
                    api_key=SecretStr("bad-secret"), http_client=http_client
                ).lookup_imdb("tt0111161")
            except ProviderAuthenticationError as exc:
                assert exc.code == "OMDB_AUTHENTICATION_FAILED"
                assert "bad-secret" not in str(exc)
            else:
                raise AssertionError("expected ProviderAuthenticationError")

    asyncio.run(run())
