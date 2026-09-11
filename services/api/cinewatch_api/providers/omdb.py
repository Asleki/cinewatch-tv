"""OMDb provider adapter for governed secondary enrichment."""

from __future__ import annotations

from typing import cast

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.errors import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderResponseError,
    ProviderUnavailableError,
)

OMDB_BASE_URL = "https://www.omdbapi.com/"


class OmdbClient:
    """Minimal server-only OMDb client; never a replacement for TMDb primary data."""

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
                provider="omdb",
                code="OMDB_CREDENTIAL_MISSING",
                message="OMDb is not configured for this runtime.",
            )
        return self._api_key.get_secret_value().strip()

    async def lookup_imdb(self, imdb_id: str) -> dict[str, object]:
        if not imdb_id.startswith("tt") or not imdb_id[2:].isdigit():
            raise ValueError("OMDb IMDb identity must have the form tt########.")

        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json", "User-Agent": "CineWatch-TV/1"},
        )
        try:
            try:
                response = await client.get(
                    OMDB_BASE_URL, params={"apikey": self._credential(), "i": imdb_id}
                )
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="omdb",
                    code="OMDB_TRANSPORT_FAILED",
                    message="OMDb could not be reached.",
                ) from exc

            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="omdb",
                    code="OMDB_UNAVAILABLE",
                    message="OMDb returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="omdb",
                    code="OMDB_REQUEST_FAILED",
                    message="OMDb rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="omdb",
                    code="OMDB_INVALID_JSON",
                    message="OMDb returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, dict):
                raise ProviderResponseError(
                    provider="omdb",
                    code="OMDB_INVALID_PAYLOAD",
                    message="OMDb returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            payload = cast(dict[str, object], payload)
            if payload.get("Response") == "False":
                message = str(payload.get("Error") or "OMDb rejected the query.")
                if "api key" in message.lower():
                    raise ProviderAuthenticationError(
                        provider="omdb",
                        code="OMDB_AUTHENTICATION_FAILED",
                        message="OMDb rejected the configured credential.",
                        status_code=response.status_code,
                    )
                raise ProviderResponseError(
                    provider="omdb",
                    code="OMDB_QUERY_FAILED",
                    message="OMDb could not satisfy the requested enrichment query.",
                    status_code=response.status_code,
                )
            return payload
        finally:
            if owns_client:
                await client.aclose()
