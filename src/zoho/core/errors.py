"""Typed SDK exceptions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ZohoError(Exception):
    """Base SDK exception."""


class ZohoAPIError(ZohoError):
    """API response error enriched with request context."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        details: Mapping[str, Any] | None = None,
        request_id: str | None = None,
        method: str | None = None,
        url: str | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = dict(details or {})
        self.request_id = request_id
        self.method = method
        self.url = url
        self.response_text = response_text

    def __str__(self) -> str:
        base = self.message
        if self.status_code is not None:
            base = f"{base} (status={self.status_code})"
        if self.code:
            base = f"{base} code={self.code}"
        if self.request_id:
            base = f"{base} request_id={self.request_id}"
        return base


class ZohoAuthError(ZohoAPIError):
    """Authentication/authorization error."""


class ZohoRateLimitError(ZohoAPIError):
    """Rate limit error."""

    def __init__(self, message: str, *, retry_after: float | None = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ZohoValidationError(ZohoAPIError):
    """Client-side or API validation error."""


class ZohoNotFoundError(ZohoAPIError):
    """Resource not found."""


class ZohoServerError(ZohoAPIError):
    """Server-side failure."""


class ZohoTransportError(ZohoError):
    """Network or transport-level exception."""
