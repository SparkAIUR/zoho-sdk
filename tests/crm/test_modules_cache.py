from __future__ import annotations

from typing import Any

from zoho.core.cache import AsyncTTLCache
from zoho.crm.client import CRMClient


async def test_modules_cache_hits() -> None:
    call_count = 0

    async def requester(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        nonlocal call_count
        _ = method
        _ = path
        _ = kwargs
        call_count += 1
        return {"modules": [{"api_name": "Leads"}]}

    crm = CRMClient(
        request=requester,
        metadata_cache=AsyncTTLCache(),
        default_metadata_ttl_seconds=60,
    )

    first = await crm.modules.list(use_cache=True)
    second = await crm.modules.list(use_cache=True)

    assert first == [{"api_name": "Leads"}]
    assert second == [{"api_name": "Leads"}]
    assert call_count == 1
