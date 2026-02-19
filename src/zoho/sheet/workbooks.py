"""Sheet workbooks APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.sheet.models import SheetResponse, parse_sheet_response

if TYPE_CHECKING:
    from zoho.sheet.client import SheetClient


class SheetWorkbooksClient:
    """Workbook operations for Zoho Sheet."""

    def __init__(self, sheet_client: SheetClient) -> None:
        self._sheet = sheet_client

    async def list(
        self,
        *,
        from_index: int | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        params: dict[str, Any] = {}
        if from_index is not None:
            params["from"] = from_index
        if limit is not None:
            params["limit"] = limit

        payload = await self._sheet.request("GET", "/workbooks", params=params, headers=headers)
        return parse_sheet_response(payload)

    async def get(
        self,
        *,
        workbook_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request("GET", f"/workbooks/{workbook_id}", headers=headers)
        return parse_sheet_response(payload)

    async def create(
        self,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request("POST", "/workbooks", json=dict(data), headers=headers)
        return parse_sheet_response(payload)

    async def delete(
        self,
        *,
        workbook_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request("DELETE", f"/workbooks/{workbook_id}", headers=headers)
        return parse_sheet_response(payload)
