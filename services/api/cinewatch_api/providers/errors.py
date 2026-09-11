"""Provider-runtime failures that never expose credentials."""

from __future__ import annotations


class ProviderError(Exception):
    """Base class for an expected external-provider failure."""

    def __init__(
        self,
        *,
        provider: str,
        code: str,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.code = code
        self.message = message
        self.status_code = status_code


class ProviderConfigurationError(ProviderError):
    """Required local provider configuration is missing."""


class ProviderAuthenticationError(ProviderError):
    """Provider rejected the supplied credential."""


class ProviderRateLimitError(ProviderError):
    """Provider rejected the request because a rate limit was reached."""


class ProviderUnavailableError(ProviderError):
    """Provider could not be reached or returned a server failure."""


class ProviderResponseError(ProviderError):
    """Provider returned an unexpected or unusable response."""
