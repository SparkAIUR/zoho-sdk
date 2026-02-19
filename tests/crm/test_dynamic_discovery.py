from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from zoho.core.cache import AsyncTTLCache
from zoho.core.discovery_cache import DiscoveryDiskCache
from zoho.crm.client import CRMClient


class _Requester:
    def __init__(self, *, raise_on_module_list: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self._raise_on_module_list = raise_on_module_list

    async def __call__(self, method: str, path: str, **_: Any) -> dict[str, Any]:
        self.calls.append((method, path))

        if method == "GET" and path == "/settings/modules":
            if self._raise_on_module_list:
                raise RuntimeError("network should not be called")
            return {"modules": [{"api_name": "Leads"}, {"api_name": "Contacts"}]}
        if method == "GET" and path == "/Leads":
            return {
                "data": [{"id": "1", "Last_Name": "Ng"}],
                "info": {"more_records": False, "page": 1},
            }
        if method == "GET" and path == "/Leads/1":
            return {"data": [{"id": "1", "Last_Name": "Ng"}]}
        if method in {"POST", "PUT", "DELETE"} and path.startswith("/Leads"):
            return {"data": [{"status": "success", "code": "SUCCESS"}]}

        return {}


def _build_crm_client(
    requester: _Requester,
    *,
    discovery_cache: DiscoveryDiskCache | None = None,
    discovery_cache_scope: str = "default:US:production",
) -> CRMClient:
    return CRMClient(
        request=requester,
        metadata_cache=AsyncTTLCache(),
        default_metadata_ttl_seconds=60,
        discovery_cache=discovery_cache,
        discovery_cache_scope=discovery_cache_scope,
    )


async def test_dynamic_attribute_binds_module_calls() -> None:
    requester = _Requester()
    crm = _build_crm_client(requester)

    leads = crm.dynamic.Leads

    listed = await leads.list(page=1, per_page=200)
    fetched = await leads.get(record_id="1")
    created = await leads.create(data={"Last_Name": "Ng"})
    updated = await leads.update(record_id="1", data={"Last_Name": "Chen"})
    deleted = await leads.delete(record_id="1")

    assert listed.data[0]["id"] == "1"
    assert fetched["Last_Name"] == "Ng"
    assert created.code == "SUCCESS"
    assert updated.code == "SUCCESS"
    assert deleted.code == "SUCCESS"
    assert ("GET", "/Leads") in requester.calls
    assert ("GET", "/Leads/1") in requester.calls
    assert ("POST", "/Leads") in requester.calls
    assert ("PUT", "/Leads") in requester.calls
    assert ("DELETE", "/Leads/1") in requester.calls


async def test_dynamic_discovery_list_and_validation() -> None:
    requester = _Requester()
    crm = _build_crm_client(requester)

    modules = await crm.dynamic.list_modules()
    assert modules == ["Leads", "Contacts"]
    assert await crm.dynamic.has_module("leads")

    leads = await crm.dynamic.get_module_client("leads")
    assert leads.module_api_name == "Leads"
    assert leads.module_metadata["api_name"] == "Leads"

    with pytest.raises(KeyError, match="Unknown CRM module"):
        await crm.dynamic.get_module_client("MissingModule")


async def test_dynamic_module_class_created_at_runtime() -> None:
    requester = _Requester()
    crm = _build_crm_client(requester)

    dynamic_leads = crm.dynamic.Leads

    assert type(dynamic_leads).__name__ == "CRMLeadsModuleClient"


async def test_dynamic_discovery_uses_disk_cache_between_processes(tmp_path: Path) -> None:
    cache = DiscoveryDiskCache(base_dir=tmp_path / "cache", ttl_seconds=3600)
    requester_a = _Requester()
    crm_a = _build_crm_client(
        requester_a,
        discovery_cache=cache,
        discovery_cache_scope="tenant_a:US:production",
    )

    modules_a = await crm_a.dynamic.list_modules(use_cache=True)
    assert modules_a == ["Leads", "Contacts"]
    assert requester_a.calls.count(("GET", "/settings/modules")) == 1

    requester_b = _Requester(raise_on_module_list=True)
    crm_b = _build_crm_client(
        requester_b,
        discovery_cache=cache,
        discovery_cache_scope="tenant_a:US:production",
    )
    modules_b = await crm_b.dynamic.list_modules(use_cache=True)
    assert modules_b == ["Leads", "Contacts"]
    assert ("GET", "/settings/modules") not in requester_b.calls
