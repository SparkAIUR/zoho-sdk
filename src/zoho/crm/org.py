"""CRM Organization operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient


class OrgClient:
    """Organization-level CRM operations."""

    def __init__(self, crm_client: CRMClient) -> None:
        self._crm = crm_client

    async def get(self) -> dict[str, Any]:
        payload = await self._crm.request("GET", "/org")
        orgs = payload.get("org")
        if isinstance(orgs, list) and orgs and isinstance(orgs[0], dict):
            return orgs[0]
        return {}
