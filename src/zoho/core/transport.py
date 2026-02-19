"""Async HTTP transport with retry and error mapping."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Mapping
from typing import Any, Protocol

import httpx

from zoho.core.errors import (
    ZohoAPIError,
    ZohoAuthError,
    ZohoNotFoundError,
    ZohoRateLimitError,
    ZohoServerError,
    ZohoTransportError,
    ZohoValidationError,
)
from zoho.core.logging import get_logger


class Transport(Protocol):
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> httpx.Response: ...


class HttpxTransport:
    """HTTPX transport with backoff retries for transient failures."""

    def __init__(
        self,
        *,
        timeout_seconds: float,
        max_connections: int,
        max_keepalive_connections: int,
        verify_ssl: bool,
        max_retries: int,
        backoff_base_seconds: float,
        backoff_max_seconds: float,
        retry_status_codes: tuple[int, ...],
    ) -> None:
        self._logger = get_logger("zoho.transport")
        self._max_retries = max_retries
        self._backoff_base_seconds = backoff_base_seconds
        self._backoff_max_seconds = backoff_max_seconds
        self._retry_status_codes = set(retry_status_codes)

        timeout = httpx.Timeout(timeout_seconds, connect=min(timeout_seconds, 10.0))
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )
        self._client = httpx.AsyncClient(timeout=timeout, limits=limits, verify=verify_ssl)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method,
                    url,
                    headers=dict(headers or {}),
                    params=dict(params or {}),
                    json=json,
                    data=data,
                    files=files,
                    timeout=timeout,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise ZohoTransportError(f"Transport request failed: {exc}") from exc
                delay = self._backoff_delay(attempt)
                self._logger.warning(
                    "transport_retry_request_error",
                    attempt=attempt + 1,
                    delay=delay,
                    error=str(exc),
                )
                await asyncio.sleep(delay)
                continue

            if self._should_retry_response(response, attempt):
                delay = self._response_retry_delay(response, attempt)
                self._logger.warning(
                    "transport_retry_response",
                    attempt=attempt + 1,
                    delay=delay,
                    status_code=response.status_code,
                )
                await asyncio.sleep(delay)
                continue

            if response.status_code >= 400:
                self._raise_for_response(method=method, url=url, response=response)

            return response

        if last_exc:
            raise ZohoTransportError(f"Transport failed after retries: {last_exc}") from last_exc
        raise ZohoTransportError("Transport failed after retries")

    def _should_retry_response(self, response: httpx.Response, attempt: int) -> bool:
        return attempt < self._max_retries and response.status_code in self._retry_status_codes

    def _response_retry_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(float(retry_after), self._backoff_max_seconds)
            except ValueError:
                pass
        return self._backoff_delay(attempt)

    def _backoff_delay(self, attempt: int) -> float:
        upper = min(self._backoff_max_seconds, self._backoff_base_seconds * (2**attempt))
        return random.uniform(self._backoff_base_seconds, upper)

    def _raise_for_response(self, *, method: str, url: str, response: httpx.Response) -> None:
        payload: Mapping[str, Any] | None = None
        try:
            maybe_payload = response.json()
            if isinstance(maybe_payload, Mapping):
                payload = maybe_payload
        except ValueError:
            payload = None

        message = "Zoho API request failed"
        if payload and isinstance(payload.get("message"), str):
            message = payload["message"]
        elif response.reason_phrase:
            message = response.reason_phrase

        code = payload.get("code") if payload else None
        details_raw = payload.get("details") if payload else None
        details = details_raw if isinstance(details_raw, Mapping) else None
        request_id = response.headers.get("X-REQUEST-ID") or response.headers.get("x-request-id")
        response_text = response.text[:500]

        kwargs = {
            "status_code": response.status_code,
            "code": str(code) if code is not None else None,
            "details": details,
            "request_id": request_id,
            "method": method,
            "url": url,
            "response_text": response_text,
        }

        if response.status_code == 401:
            raise ZohoAuthError(message, **kwargs)
        if response.status_code == 404:
            raise ZohoNotFoundError(message, **kwargs)
        if response.status_code == 429:
            retry_after: float | None = None
            retry_after_raw = response.headers.get("Retry-After")
            if retry_after_raw:
                try:
                    retry_after = float(retry_after_raw)
                except ValueError:
                    retry_after = None
            raise ZohoRateLimitError(message, retry_after=retry_after, **kwargs)
        if response.status_code == 400:
            raise ZohoValidationError(message, **kwargs)
        if response.status_code >= 500:
            raise ZohoServerError(message, **kwargs)
        raise ZohoAPIError(message, **kwargs)
