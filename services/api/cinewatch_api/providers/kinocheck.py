"""Server-only KinoCheck adapter for official trailer/video discovery."""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

import httpx
from pydantic import SecretStr

from cinewatch_api.providers.errors import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
)

KINOCHECK_BASE_URL = "https://api.kinocheck.com"


class KinoCheckClient:
    """KinoCheck client; public allowance works without a key, higher quotas may use one."""

    def __init__(
        self,
        *,
        api_key: SecretStr | None = None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._client = http_client
        self._timeout_seconds = timeout_seconds

    async def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | bool] | None = None,
    ) -> dict[str, object] | list[object]:
        if not path.startswith("/"):
            raise ValueError("KinoCheck path must start with '/'.")
        headers = {"Accept": "application/json", "User-Agent": "CineWatch-TV/1"}
        if self._api_key is not None and self._api_key.get_secret_value().strip():
            headers["X-Api-Key"] = self._api_key.get_secret_value().strip()
            headers["X-Api-Host"] = "api.kinocheck.com"
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self._timeout_seconds)
        try:
            try:
                response = await client.get(
                    f"{KINOCHECK_BASE_URL}{path}", params=dict(params or {}), headers=headers
                )
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="kinocheck",
                    code="KINOCHECK_TRANSPORT_FAILED",
                    message="KinoCheck could not be reached.",
                ) from exc
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="kinocheck",
                    code="KINOCHECK_AUTHENTICATION_FAILED",
                    message="KinoCheck rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="kinocheck",
                    code="KINOCHECK_RATE_LIMITED",
                    message="KinoCheck rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="kinocheck",
                    code="KINOCHECK_UNAVAILABLE",
                    message="KinoCheck returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="kinocheck",
                    code="KINOCHECK_REQUEST_FAILED",
                    message="KinoCheck rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="kinocheck",
                    code="KINOCHECK_INVALID_JSON",
                    message="KinoCheck returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, (dict, list)):
                raise ProviderResponseError(
                    provider="kinocheck",
                    code="KINOCHECK_INVALID_PAYLOAD",
                    message="KinoCheck returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            return cast(dict[str, object] | list[object], payload)
        finally:
            if owns_client:
                await client.aclose()
