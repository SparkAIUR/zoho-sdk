"""WorkDrive folder APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.workdrive.models import WorkDriveResponse, parse_workdrive_response

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient


class WorkDriveFoldersClient:
    """Folder operations for Zoho WorkDrive."""

    def __init__(self, workdrive_client: WorkDriveClient) -> None:
        self._workdrive = workdrive_client

    async def list_children(
        self,
        *,
        folder_id: str,
        offset: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        params: dict[str, Any] = {}
        if offset is not None:
            params["page[offset]"] = offset
        if limit is not None:
            params["page[limit]"] = limit
        if cursor is not None:
            params["page[next]"] = cursor

        payload = await self._workdrive.request(
            "GET",
            f"/api/v1/files/{folder_id}/files",
            params=params,
            headers=headers,
        )
        return parse_workdrive_response(payload)

    async def create(
        self,
        *,
        parent_id: str,
        name: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "POST",
            "/api/v1/folders",
            json={"data": {"type": "files", "attributes": {"name": name, "parent_id": parent_id}}},
            headers=headers,
        )
        return parse_workdrive_response(payload)

    async def rename(
        self,
        *,
        folder_id: str,
        name: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "PATCH",
            f"/api/v1/files/{folder_id}",
            json={"data": {"attributes": {"name": name}}},
            headers=headers,
        )
        return parse_workdrive_response(payload)
