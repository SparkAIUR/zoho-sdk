from __future__ import annotations

from pathlib import Path
from typing import Any

from zoho.core.discovery_cache import DiscoveryDiskCache
from zoho.creator.client import CreatorClient
from zoho.creator.models import CreatorResponse


class _Requester:
    def __init__(self, *, raise_on_app_list: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self._raise_on_app_list = raise_on_app_list

    async def __call__(self, method: str, path: str, **_: Any) -> dict[str, Any]:
        self.calls.append((method, path))

        if method == "GET" and path == "/creator/v2/meta/applications":
            if self._raise_on_app_list:
                raise RuntimeError("network should not be called")
            return {
                "code": 3000,
                "applications": [
                    {
                        "application_name": "Inventory",
                        "link_name": "inventory-app",
                        "workspace_name": "owner",
                    },
                    {
                        "application_name": "HR",
                        "link_name": "hr_app",
                        "workspace_name": "owner",
                    },
                ],
            }

        if method == "GET" and path == "/meta/owner/inventory-app/forms":
            return {"code": 3000, "data": [{"link_name": "orders"}]}
        if method == "GET" and path == "/data/owner/inventory-app/report/all_orders":
            return {"code": 3000, "data": [{"id": "1"}]}
        if method == "GET" and path == "/publish/owner/inventory-app/report/all_orders":
            return {"code": 3000, "data": [{"id": "1"}]}

        return {"code": 3000, "data": []}


async def test_creator_dynamic_discovery_and_bound_clients() -> None:
    requester = _Requester()
    creator = CreatorClient(request=requester)

    applications = await creator.dynamic.list_applications()

    assert len(applications) == 2
    assert await creator.dynamic.has_application("inventory_app")

    app = await creator.dynamic.get_application_client("owner.inventory-app")
    forms = await app.meta.get_forms()
    data_rows = await app.data.list_records(report_link_name="all_orders")
    published_rows = await app.publish.list_records(report_link_name="all_orders")

    assert isinstance(forms, CreatorResponse)
    assert isinstance(data_rows, CreatorResponse)
    assert isinstance(published_rows, CreatorResponse)
    assert forms.data[0].model_dump(mode="python")["link_name"] == "orders"
    assert type(creator.dynamic.inventory_app).__name__ == "CreatorInventoryAppApplicationClient"

    assert ("GET", "/creator/v2/meta/applications") in requester.calls
    assert ("GET", "/meta/owner/inventory-app/forms") in requester.calls
    assert ("GET", "/data/owner/inventory-app/report/all_orders") in requester.calls
    assert ("GET", "/publish/owner/inventory-app/report/all_orders") in requester.calls


async def test_creator_dynamic_discovery_uses_disk_cache(tmp_path: Path) -> None:
    cache = DiscoveryDiskCache(base_dir=tmp_path / "cache", ttl_seconds=3600)

    requester_a = _Requester()
    creator_a = CreatorClient(
        request=requester_a,
        discovery_cache=cache,
        discovery_cache_scope="tenant_a:US:production",
    )
    applications_a = await creator_a.dynamic.list_applications(use_cache=True)
    assert len(applications_a) == 2

    requester_b = _Requester(raise_on_app_list=True)
    creator_b = CreatorClient(
        request=requester_b,
        discovery_cache=cache,
        discovery_cache_scope="tenant_a:US:production",
    )
    applications_b = await creator_b.dynamic.list_applications(use_cache=True)

    assert len(applications_b) == 2
    assert ("GET", "/creator/v2/meta/applications") not in requester_b.calls
