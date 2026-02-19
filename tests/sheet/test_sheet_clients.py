from __future__ import annotations

from typing import Any

from zoho.sheet.client import SheetClient
from zoho.sheet.models import SheetResponse


class DummySheetRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        if path.endswith("/records"):
            return {"records": [{"id": "r1", "name": "Row 1"}]}
        return {"workbooks": [{"id": "wb1", "name": "Main"}]}


async def test_sheet_workbook_and_tabular_paths() -> None:
    request = DummySheetRequest()
    sheet = SheetClient(request=request)

    workbooks = await sheet.workbooks.list()
    records = await sheet.tabular.fetch_worksheet_records(
        workbook_id="wb1",
        worksheet_name="Sheet1",
        limit=200,
    )

    assert isinstance(workbooks, SheetResponse)
    assert isinstance(records, SheetResponse)

    paths = [call["path"] for call in request.calls]
    assert "/workbooks" in paths
    assert "/workbooks/wb1/worksheets/Sheet1/records" in paths
