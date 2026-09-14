"""Server-only Watchmode adapter for external availability discovery."""

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

WATCHMODE_BASE_URL = "https://api.watchmode.com/v1"


class WatchmodeClient:
    """Minimal Watchmode client; never grants CineWatch playback authority."""

    def __init__(
        self,
        *,
        api_key: SecretStr | None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._client = http_client
        self._timeout_seconds = timeout_seconds

    def _credential(self) -> str:
        if self._api_key is None or not self._api_key.get_secret_value().strip():
            raise ProviderConfigurationError(
                provider="watchmode",
                code="WATCHMODE_CREDENTIAL_MISSING",
                message="Watchmode is not configured for this runtime.",
            )
        return self._api_key.get_secret_value().strip()

    async def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, str | int | bool] | None = None,
    ) -> dict[str, object] | list[object]:
        if not path.startswith("/"):
            raise ValueError("Watchmode path must start with '/'.")
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json", "User-Agent": "CineWatch-TV/1"},
        )
        try:
            try:
                response = await client.get(
                    f"{WATCHMODE_BASE_URL}{path}",
                    params=dict(params or {}),
                    headers={"X-API-Key": self._credential()},
                )
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="watchmode",
                    code="WATCHMODE_TRANSPORT_FAILED",
                    message="Watchmode could not be reached.",
                ) from exc
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="watchmode",
                    code="WATCHMODE_AUTHENTICATION_FAILED",
                    message="Watchmode rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="watchmode",
                    code="WATCHMODE_RATE_LIMITED",
                    message="Watchmode rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="watchmode",
                    code="WATCHMODE_UNAVAILABLE",
                    message="Watchmode returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="watchmode",
                    code="WATCHMODE_REQUEST_FAILED",
                    message="Watchmode rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="watchmode",
                    code="WATCHMODE_INVALID_JSON",
                    message="Watchmode returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, (dict, list)):
                raise ProviderResponseError(
                    provider="watchmode",
                    code="WATCHMODE_INVALID_PAYLOAD",
                    message="Watchmode returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            return cast(dict[str, object] | list[object], payload)
        finally:
            if owns_client:
                await client.aclose()
