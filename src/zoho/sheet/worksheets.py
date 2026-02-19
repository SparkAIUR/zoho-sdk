"""Sheet worksheet APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.sheet.models import SheetResponse, parse_sheet_response

if TYPE_CHECKING:
    from zoho.sheet.client import SheetClient


class SheetWorksheetsClient:
    """Worksheet operations for Zoho Sheet."""

    def __init__(self, sheet_client: SheetClient) -> None:
        self._sheet = sheet_client

    async def list(
        self,
        *,
        workbook_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "GET",
            f"/workbooks/{workbook_id}/worksheets",
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def create(
        self,
        *,
        workbook_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "POST",
            f"/workbooks/{workbook_id}/worksheets",
            json=dict(data),
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def rename(
        self,
        *,
        workbook_id: str,
        worksheet_id: str,
        name: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "PATCH",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_id}",
            json={"name": name},
            headers=headers,
        )
        return parse_sheet_response(payload)

    async def delete(
        self,
        *,
        workbook_id: str,
        worksheet_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> SheetResponse:
        payload = await self._sheet.request(
            "DELETE",
            f"/workbooks/{workbook_id}/worksheets/{worksheet_id}",
            headers=headers,
        )
        return parse_sheet_response(payload)
