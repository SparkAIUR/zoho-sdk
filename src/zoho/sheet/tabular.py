"""Sheet tabular data APIs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.sheet.models import SheetResponse, parse_sheet_response

if TYPE_CHECKING:
    from zoho.sheet.client import SheetClient


class SheetTabularClient:
    """Record operations for worksheet/table-style access."""

    def __init__(self, sheet_client: SheetClient) -> None:
        self._sheet = sheet_client

    async def fetch_worksheet_records(
        self,
        *,
        workbook_id: str,
        worksheet_name: str,
        offset: int | None = None,
        limit: int | None = None,
        criteria: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if criteria is not None:
            params["criteria"] = criteria

        payload = await self._sheet.request(
            "GET",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_name}/records",
            params=params,
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def add_worksheet_records(
        self,
        *,
        workbook_id: str,
        worksheet_name: str,
        records: Sequence[Mapping[str, Any]],
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "POST",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_name}/records",
            json={"records": [dict(row) for row in records]},
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def update_worksheet_records(
        self,
        *,
        workbook_id: str,
        worksheet_name: str,
        criteria: str,
        updates: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "PATCH",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_name}/records",
            json={"criteria": criteria, "data": dict(updates)},
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def delete_worksheet_records(
        self,
        *,
        workbook_id: str,
        worksheet_name: str,
        criteria: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "DELETE",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_name}/records",
            params={"criteria": criteria},
            headers=headers,
        )
        return parse_sheet_response(payload)
