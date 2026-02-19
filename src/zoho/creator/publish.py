"""Creator publish API operations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.creator.models import CreatorResponse, parse_creator_response

if TYPE_CHECKING:
    from zoho.creator.client import CreatorClient


class CreatorPublishClient:
    """Creator publish APIs for public/private app endpoints.

    Example:
        ```python
        response = await zoho.creator.publish.list_records(
            account_owner_name="owner",
            app_link_name="inventory_app",
            report_link_name="all_orders",
        )
        print(response.first_data)
        ```
    """

    def __init__(self, creator_client: CreatorClient) -> None:
        self._creator = creator_client

    async def list_records(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        report_link_name: str,
        from_index: int | None = None,
        limit: int | None = None,
        criteria: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        params: dict[str, Any] = {}
        if from_index is not None:
            params["from"] = from_index
        if limit is not None:
            params["limit"] = limit
        if criteria is not None:
            params["criteria"] = criteria

        payload = await self._creator.request(
            "GET",
            f"/publish/{account_owner_name}/{app_link_name}/report/{report_link_name}",
            params=params,
            headers=headers,
        )
        return parse_creator_response(payload)

    async def add_records(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        form_link_name: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        rows = [dict(data)] if isinstance(data, Mapping) else [dict(item) for item in data]
        payload: dict[str, Any] = {"data": rows}

        response = await self._creator.request(
            "POST",
            f"/publish/{account_owner_name}/{app_link_name}/form/{form_link_name}",
            json=payload,
            headers=headers,
        )
        return parse_creator_response(response)

    async def update_record(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        report_link_name: str,
        record_id: str | int,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "PATCH",
            f"/publish/{account_owner_name}/{app_link_name}/report/{report_link_name}/{record_id}",
            json={"data": dict(data)},
            headers=headers,
        )
        return parse_creator_response(payload)

    async def delete_record(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        report_link_name: str,
        record_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "DELETE",
            f"/publish/{account_owner_name}/{app_link_name}/report/{report_link_name}/{record_id}",
            headers=headers,
        )
        return parse_creator_response(payload)
