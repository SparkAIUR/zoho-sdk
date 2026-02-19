"""CRM Modules metadata operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient


class ModulesClient:
    """CRM module metadata operations."""

    def __init__(self, crm_client: CRMClient) -> None:
        self._crm = crm_client

    async def list(
        self,
        *,
        use_cache: bool = True,
        cache_ttl_seconds: int | None = None,
    ) -> list[dict[str, Any]]:
        payload = await self._crm.request(
            "GET",
            "/settings/modules",
            use_cache=use_cache,
            cache_key="crm:settings:modules:list",
            cache_ttl_seconds=cache_ttl_seconds,
        )
        data = payload.get("modules")
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []

    async def get(
        self,
        module: str,
        *,
        use_cache: bool = True,
        cache_ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        payload = await self._crm.request(
            "GET",
            f"/settings/modules/{module}",
            use_cache=use_cache,
            cache_key=f"crm:settings:modules:get:{module}",
            cache_ttl_seconds=cache_ttl_seconds,
        )
        modules = payload.get("modules")
        if isinstance(modules, list) and modules and isinstance(modules[0], dict):
            return modules[0]
        return {}
