"""Apify adapter for the explicitly configured screenplay discovery Actor."""

from __future__ import annotations

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

APIFY_SCREENPLAY_URL = (
    "https://api.apify.com/v2/actors/"
    "thescrapelab~screenplay-script-scraper/run-sync-get-dataset-items"
)


class ApifyScreenplayClient:
    def __init__(
        self,
        *,
        token: SecretStr | None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        self._token = token
        self._client = http_client
        self._timeout_seconds = timeout_seconds

    def _credential(self) -> str:
        if self._token is None or not self._token.get_secret_value().strip():
            raise ProviderConfigurationError(
                provider="apify_screenplay",
                code="APIFY_SCREENPLAY_CREDENTIAL_MISSING",
                message="Apify screenplay discovery is not configured for this runtime.",
            )
        return self._token.get_secret_value().strip()

    async def search_title(self, title: str) -> list[dict[str, object]]:
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json", "User-Agent": "CineWatch-TV/1"},
        )
        try:
            try:
                response = await client.post(
                    APIFY_SCREENPLAY_URL,
                    params={"clean": "true"},
                    headers={"Authorization": f"Bearer {self._credential()}"},
                    json={"movieName": title},
                )
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_TRANSPORT_FAILED",
                    message="Apify screenplay discovery could not be reached.",
                ) from exc
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_AUTHENTICATION_FAILED",
                    message="Apify rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_RATE_LIMITED",
                    message="Apify rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_UNAVAILABLE",
                    message="Apify returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_REQUEST_FAILED",
                    message="Apify rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_INVALID_JSON",
                    message="Apify returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, list):
                raise ProviderResponseError(
                    provider="apify_screenplay",
                    code="APIFY_SCREENPLAY_INVALID_PAYLOAD",
                    message="Apify returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            return [cast(dict[str, object], row) for row in payload if isinstance(row, dict)]
        finally:
            if owns_client:
                await client.aclose()
