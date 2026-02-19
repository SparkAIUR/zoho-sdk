from __future__ import annotations

from typing import Any

import pytest

from zoho.core.cache import AsyncTTLCache
from zoho.crm.client import CRMClient


class _Requester:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    async def __call__(self, method: str, path: str, **_: Any) -> dict[str, Any]:
        self.calls.append((method, path))

        if method == "GET" and path == "/settings/modules":
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


def _build_crm_client(requester: _Requester) -> CRMClient:
    return CRMClient(
        request=requester,
        metadata_cache=AsyncTTLCache(),
        default_metadata_ttl_seconds=60,
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
