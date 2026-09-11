"""TMDb provider adapter. TMDb is CineWatch's primary entertainment-data upstream."""

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

TMDB_BASE_URL = "https://api.themoviedb.org/3"


class TmdbClient:
    """Minimal server-only TMDb client used by governed CineWatch services."""

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
                provider="tmdb",
                code="TMDB_CREDENTIAL_MISSING",
                message="TMDb is not configured for this runtime.",
            )
        return self._api_key.get_secret_value().strip()

    async def get_json(
        self, path: str, *, params: Mapping[str, str | int | float | bool] | None = None
    ) -> dict[str, object]:
        if not path.startswith("/"):
            raise ValueError("TMDb path must start with '/'.")

        query: dict[str, str | int | float | bool] = dict(params or {})
        query["api_key"] = self._credential()
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json", "User-Agent": "CineWatch-TV/1"},
        )
        try:
            try:
                response = await client.get(f"{TMDB_BASE_URL}{path}", params=query)
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="tmdb",
                    code="TMDB_TRANSPORT_FAILED",
                    message="TMDb could not be reached.",
                ) from exc

            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="tmdb",
                    code="TMDB_AUTHENTICATION_FAILED",
                    message="TMDb rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="tmdb",
                    code="TMDB_RATE_LIMITED",
                    message="TMDb rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="tmdb",
                    code="TMDB_UNAVAILABLE",
                    message="TMDb returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="tmdb",
                    code="TMDB_REQUEST_FAILED",
                    message="TMDb rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="tmdb",
                    code="TMDB_INVALID_JSON",
                    message="TMDb returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, dict):
                raise ProviderResponseError(
                    provider="tmdb",
                    code="TMDB_INVALID_PAYLOAD",
                    message="TMDb returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            return cast(dict[str, object], payload)
        finally:
            if owns_client:
                await client.aclose()

    async def configuration(self) -> dict[str, object]:
        """Perform a low-cost authenticated probe without exposing the credential."""

        return await self.get_json("/configuration")
