from __future__ import annotations

import httpx
import pytest

from zoho.core.errors import ZohoNotFoundError
from zoho.core.transport import HttpxTransport


async def test_transport_retries_retryable_status() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        _ = request
        attempts += 1
        if attempts == 1:
            return httpx.Response(500, json={"message": "temporary"})
        return httpx.Response(200, json={"ok": True})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HttpxTransport(
        timeout_seconds=5.0,
        max_connections=10,
        max_keepalive_connections=5,
        verify_ssl=True,
        max_retries=1,
        backoff_base_seconds=0.01,
        backoff_max_seconds=0.02,
        retry_status_codes=(500,),
    )
    # Inject mock client for deterministic testing.
    transport._client = client  # type: ignore[attr-defined]

    response = await transport.request("GET", "https://example.test/resource")

    assert response.status_code == 200
    assert attempts == 2

    await transport.close()


async def test_transport_maps_not_found_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        _ = request
        return httpx.Response(404, json={"message": "missing"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = HttpxTransport(
        timeout_seconds=5.0,
        max_connections=10,
        max_keepalive_connections=5,
        verify_ssl=True,
        max_retries=0,
        backoff_base_seconds=0.01,
        backoff_max_seconds=0.02,
        retry_status_codes=(500,),
    )
    transport._client = client  # type: ignore[attr-defined]

    with pytest.raises(ZohoNotFoundError):
        await transport.request("GET", "https://example.test/missing")

    await transport.close()
