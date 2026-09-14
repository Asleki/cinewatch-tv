"""Server-only NewsAPI provider adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.errors import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
)

NEWS_API_BASE_URL = "https://newsapi.org/v2"


class NewsApiClient:
    def __init__(
        self,
        *,
        api_key: SecretStr | None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 8.0,
    ) -> None:
        self._api_key = api_key
        self._client = http_client
        self._timeout_seconds = timeout_seconds

    def _credential(self) -> str:
        if self._api_key is None or not self._api_key.get_secret_value().strip():
            raise ProviderConfigurationError(
                provider="newsapi",
                code="NEWSAPI_CREDENTIAL_MISSING",
                message="NewsAPI is not configured for this runtime.",
            )
        return self._api_key.get_secret_value().strip()

    async def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | bool] | None = None,
    ) -> dict[str, object]:
        if not path.startswith("/"):
            raise ValueError("NewsAPI path must start with '/'.")
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={
                "Accept": "application/json",
                "User-Agent": "CineWatch-TV/1",
                "X-Api-Key": self._credential(),
            },
        )
        try:
            try:
                response = await client.get(
                    f"{NEWS_API_BASE_URL}{path}",
                    params=dict(params or {}),
                    headers={"X-Api-Key": self._credential()},
                )
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="newsapi",
                    code="NEWSAPI_TRANSPORT_FAILED",
                    message="NewsAPI could not be reached.",
                ) from exc
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="newsapi",
                    code="NEWSAPI_AUTHENTICATION_FAILED",
                    message="NewsAPI rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="newsapi",
                    code="NEWSAPI_RATE_LIMITED",
                    message="NewsAPI rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="newsapi",
                    code="NEWSAPI_UNAVAILABLE",
                    message="NewsAPI returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="newsapi",
                    code="NEWSAPI_REQUEST_FAILED",
                    message="NewsAPI rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="newsapi",
                    code="NEWSAPI_INVALID_JSON",
                    message="NewsAPI returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, dict):
                raise ProviderResponseError(
                    provider="newsapi",
                    code="NEWSAPI_INVALID_PAYLOAD",
                    message="NewsAPI returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            payload = cast(dict[str, object], payload)
            if payload.get("status") != "ok":
                raise ProviderResponseError(
                    provider="newsapi",
                    code="NEWSAPI_QUERY_FAILED",
                    message="NewsAPI could not satisfy the request.",
                    status_code=response.status_code,
                )
            return payload
        finally:
            if owns_client:
                await client.aclose()
