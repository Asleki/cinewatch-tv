"""STANDS4 service adapters used only through CineWatch's server boundary."""

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

STANDS4_LYRICS_URL = "https://www.stands4.com/services/v2/lyrics.php"


class Stands4LyricsClient:
    def __init__(
        self,
        *,
        user_id: SecretStr | None,
        token: SecretStr | None,
        http_client: httpx.AsyncClient | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self._user_id = user_id
        self._token = token
        self._client = http_client
        self._timeout_seconds = timeout_seconds

    def _credentials(self) -> tuple[str, str]:
        uid = self._user_id.get_secret_value().strip() if self._user_id else ""
        token = self._token.get_secret_value().strip() if self._token else ""
        if not uid or not token:
            raise ProviderConfigurationError(
                provider="stands4_lyrics",
                code="STANDS4_LYRICS_CREDENTIAL_MISSING",
                message="STANDS4 Lyrics is not configured for this runtime.",
            )
        return uid, token

    async def search(self, term: str, artist: str) -> dict[str, object]:
        uid, token = self._credentials()
        query: dict[str, str] = {
            "uid": uid,
            "tokenid": token,
            "term": term,
            "artist": artist,
            "format": "json",
        }
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json", "User-Agent": "CineWatch-TV/1"},
        )
        try:
            try:
                response = await client.get(STANDS4_LYRICS_URL, params=query)
            except httpx.HTTPError as exc:
                raise ProviderUnavailableError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_TRANSPORT_FAILED",
                    message="STANDS4 Lyrics could not be reached.",
                ) from exc
            if response.status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_AUTHENTICATION_FAILED",
                    message="STANDS4 Lyrics rejected the configured credential.",
                    status_code=response.status_code,
                )
            if response.status_code == 429:
                raise ProviderRateLimitError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_RATE_LIMITED",
                    message="STANDS4 Lyrics rate-limited the request.",
                    status_code=429,
                )
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_UNAVAILABLE",
                    message="STANDS4 Lyrics returned a server failure.",
                    status_code=response.status_code,
                )
            if not response.is_success:
                raise ProviderResponseError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_REQUEST_FAILED",
                    message="STANDS4 Lyrics rejected the request.",
                    status_code=response.status_code,
                )
            try:
                payload = response.json()
            except ValueError as exc:
                raise ProviderResponseError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_INVALID_JSON",
                    message="STANDS4 Lyrics returned invalid JSON.",
                    status_code=response.status_code,
                ) from exc
            if not isinstance(payload, dict):
                raise ProviderResponseError(
                    provider="stands4_lyrics",
                    code="STANDS4_LYRICS_INVALID_PAYLOAD",
                    message="STANDS4 Lyrics returned an unexpected payload shape.",
                    status_code=response.status_code,
                )
            return cast(dict[str, object], payload)
        finally:
            if owns_client:
                await client.aclose()
