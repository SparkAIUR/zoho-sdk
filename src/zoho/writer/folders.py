"""Writer folder APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.writer.models import WriterResponse, parse_writer_response

if TYPE_CHECKING:
    from zoho.writer.client import WriterClient


class WriterFoldersClient:
    """Folder operations for Zoho Writer."""

    def __init__(self, writer_client: WriterClient) -> None:
        self._writer = writer_client

    async def list(
        self,
        *,
        parent_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        params: dict[str, Any] = {}
        if parent_id:
            params["parent_id"] = parent_id
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        payload = await self._writer.request("GET", "/folders", params=params, headers=headers)
        return parse_writer_response(payload)

    async def get(
        self,
        *,
        folder_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request("GET", f"/folders/{folder_id}", headers=headers)
        return parse_writer_response(payload)

    async def create(
        self,
        *,
        name: str,
        parent_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        data: dict[str, Any] = {"name": name}
        if parent_id is not None:
            data["parent_id"] = parent_id

        payload = await self._writer.request("POST", "/folders", json=data, headers=headers)
        return parse_writer_response(payload)

    async def update(
        self,
        *,
        folder_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "PUT",
            f"/folders/{folder_id}",
            json=dict(data),
            headers=headers,
        )
        return parse_writer_response(payload)

    async def delete(
        self,
        *,
        folder_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request("DELETE", f"/folders/{folder_id}", headers=headers)
        return parse_writer_response(payload)
