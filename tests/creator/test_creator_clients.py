from __future__ import annotations

from typing import Any

from zoho.creator.client import CreatorClient
from zoho.creator.models import CreatorResponse


class DummyCreatorRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        if "/meta/" in path:
            return {"code": 3000, "data": [{"name": "Field"}]}
        return {"code": 3000, "data": [{"id": "1"}]}


async def test_creator_meta_endpoints() -> None:
    request = DummyCreatorRequest()
    creator = CreatorClient(request=request)

    sections = await creator.meta.get_sections(account_owner_name="owner", app_link_name="app")
    await creator.meta.get_forms(account_owner_name="owner", app_link_name="app")
    await creator.meta.get_reports(account_owner_name="owner", app_link_name="app")
    await creator.meta.get_form_fields(
        account_owner_name="owner",
        app_link_name="app",
        form_link_name="orders",
    )

    assert isinstance(sections, CreatorResponse)
    assert sections.data

    paths = [call["path"] for call in request.calls]
    assert "/meta/owner/app/sections" in paths
    assert "/meta/owner/app/forms" in paths
    assert "/meta/owner/app/reports" in paths
    assert "/meta/owner/app/form/orders/fields" in paths


async def test_creator_data_and_publish_endpoints() -> None:
    request = DummyCreatorRequest()
    creator = CreatorClient(request=request)

    records = await creator.data.list_records(
        account_owner_name="owner",
        app_link_name="app",
        report_link_name="all_orders",
        from_index=1,
        limit=10,
    )
    await creator.data.add_records(
        account_owner_name="owner",
        app_link_name="app",
        form_link_name="orders",
        data={"Name": "A"},
    )
    await creator.publish.add_records(
        account_owner_name="owner",
        app_link_name="app",
        form_link_name="orders",
        data={"Name": "B"},
    )

    assert isinstance(records, CreatorResponse)

    paths = [call["path"] for call in request.calls]
    assert "/data/owner/app/report/all_orders" in paths
    assert "/data/owner/app/form/orders" in paths
    assert "/publish/owner/app/form/orders" in paths
