from __future__ import annotations

from typing import Any

from zoho.crm.records import RecordsClient


class DummyCRM:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})

        params = kwargs.get("params") or {}
        page = int(params.get("page", 1))

        if method == "GET" and path == "/Leads/1":
            return {"data": [{"id": "1", "Last_Name": "Ng"}]}
        if method == "GET" and path == "/Leads" and page == 1:
            return {
                "data": [{"id": "1"}, {"id": "2"}],
                "info": {"more_records": True, "page": 1},
            }
        if method == "GET" and path == "/Leads" and page == 2:
            return {
                "data": [{"id": "3"}],
                "info": {"more_records": False, "page": 2},
            }
        if method in {"POST", "PUT", "DELETE"}:
            return {"data": [{"status": "success", "code": "SUCCESS"}]}
        return {}


async def test_records_get() -> None:
    crm = DummyCRM()
    records = RecordsClient(crm)

    lead = await records.get(module="Leads", record_id="1", fields=["Last_Name"])

    assert lead.id == "1"
    assert lead["Last_Name"] == "Ng"


async def test_records_iterates_pages() -> None:
    crm = DummyCRM()
    records = RecordsClient(crm)

    ids = [record.id async for record in records.iter(module="Leads", per_page=2)]

    assert ids == ["1", "2", "3"]


async def test_records_create_update_delete() -> None:
    crm = DummyCRM()
    records = RecordsClient(crm)

    created = await records.create(module="Leads", data={"Last_Name": "Ng"})
    updated = await records.update(module="Leads", record_id="1", data={"Last_Name": "Chen"})
    deleted = await records.delete(module="Leads", record_id="1")

    assert created.code == "SUCCESS"
    assert updated.code == "SUCCESS"
    assert deleted.code == "SUCCESS"
