"""Zoho Sheet product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.sheet.tabular import SheetTabularClient
    from zoho.sheet.workbooks import SheetWorkbooksClient
    from zoho.sheet.worksheets import SheetWorksheetsClient


class SheetRequestCallable(Protocol):
    async def __call__(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]: ...


class SheetClient:
    """Product-scoped Sheet client."""

    def __init__(self, *, request: SheetRequestCallable) -> None:
        self._request_fn = request
        self._workbooks: SheetWorkbooksClient | None = None
        self._worksheets: SheetWorksheetsClient | None = None
        self._tabular: SheetTabularClient | None = None

    @property
    def workbooks(self) -> SheetWorkbooksClient:
        if self._workbooks is None:
            from zoho.sheet.workbooks import SheetWorkbooksClient

            self._workbooks = SheetWorkbooksClient(self)
        return self._workbooks

    @property
    def worksheets(self) -> SheetWorksheetsClient:
        if self._worksheets is None:
            from zoho.sheet.worksheets import SheetWorksheetsClient

            self._worksheets = SheetWorksheetsClient(self)
        return self._worksheets

    @property
    def tabular(self) -> SheetTabularClient:
        if self._tabular is None:
            from zoho.sheet.tabular import SheetTabularClient

            self._tabular = SheetTabularClient(self)
        return self._tabular

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return await self._request_fn(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
