"""CRM Record operations."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.core.pagination import AsyncPager, Page
from zoho.crm.models import ActionResponse, PageInfo, Record, RecordListResponse, extract_first_data

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient


class RecordsClient:
    """High-usage CRM record operations.

    Example:
        ```python
        lead = await zoho.crm.records.get(module="Leads", record_id="123")
        await zoho.crm.records.update(module="Leads", record_id="123", data={"Last_Name": "Ng"})
        async for rec in zoho.crm.records.iter(module="Leads", fields=["Email", "Last_Name"]):
            print(rec["Email"])
        ```
    """

    def __init__(self, crm_client: CRMClient) -> None:
        self._crm = crm_client

    async def get(
        self,
        *,
        module: str,
        record_id: str | int,
        fields: Sequence[str] | None = None,
    ) -> Record:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = ",".join(fields)

        payload = await self._crm.request("GET", f"/{module}/{record_id}", params=params)
        return Record(extract_first_data(payload))

    async def list(
        self,
        *,
        module: str,
        page: int = 1,
        per_page: int = 200,
        fields: Sequence[str] | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> RecordListResponse:
        params: dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        if fields:
            params["fields"] = ",".join(fields)
        if extra_params:
            params.update(extra_params)

        payload = await self._crm.request("GET", f"/{module}", params=params)
        data_raw = payload.get("data")
        data = (
            [item for item in data_raw if isinstance(item, dict)]
            if isinstance(data_raw, list)
            else []
        )

        info_raw = payload.get("info")
        info = PageInfo.model_validate(info_raw) if isinstance(info_raw, dict) else None
        return RecordListResponse(data=data, info=info)

    async def iter(
        self,
        *,
        module: str,
        per_page: int = 200,
        fields: Sequence[str] | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> AsyncIterator[Record]:
        async def fetch_page(page: int, page_size: int) -> Page[Record]:
            result = await self.list(
                module=module,
                page=page,
                per_page=page_size,
                fields=fields,
                extra_params=extra_params,
            )
            records = [Record(item) for item in result.data]
            has_more = (
                bool(result.info.more_records)
                if result.info is not None
                else len(records) == page_size
            )
            next_page = page + 1 if has_more else None
            return Page(items=records, has_more=has_more, next_page=next_page)

        pager = AsyncPager(fetch_page=fetch_page, page_size=per_page)
        async for item in pager:
            yield item

    async def create(
        self,
        *,
        module: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        trigger: Sequence[str] | None = None,
    ) -> ActionResponse:
        rows = [dict(data)] if isinstance(data, Mapping) else [dict(item) for item in data]
        payload: dict[str, Any] = {"data": rows}
        if trigger:
            payload["trigger"] = list(trigger)

        response = await self._crm.request("POST", f"/{module}", json=payload)
        return ActionResponse.model_validate(extract_first_data(response))

    async def update(
        self,
        *,
        module: str,
        record_id: str | int,
        data: Mapping[str, Any],
        trigger: Sequence[str] | None = None,
    ) -> ActionResponse:
        row = {"id": str(record_id), **dict(data)}
        payload: dict[str, Any] = {"data": [row]}
        if trigger:
            payload["trigger"] = list(trigger)

        response = await self._crm.request("PUT", f"/{module}", json=payload)
        return ActionResponse.model_validate(extract_first_data(response))

    async def delete(self, *, module: str, record_id: str | int) -> ActionResponse:
        response = await self._crm.request("DELETE", f"/{module}/{record_id}")
        return ActionResponse.model_validate(extract_first_data(response))
