"""WorkDrive file APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from zoho.workdrive.models import WorkDriveResponse, parse_workdrive_response

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient


class WorkDriveFilesClient:
    """File operations for Zoho WorkDrive."""

    def __init__(self, workdrive_client: WorkDriveClient) -> None:
        self._workdrive = workdrive_client

    async def get(
        self, *, file_id: str, headers: Mapping[str, str] | None = None
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request("GET", f"/api/v1/files/{file_id}", headers=headers)
        return parse_workdrive_response(payload)

    async def trash(
        self,
        *,
        file_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "POST", f"/api/v1/files/{file_id}/trash", headers=headers
        )
        return parse_workdrive_response(payload)

    async def restore(
        self,
        *,
        file_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "POST", f"/api/v1/files/{file_id}/restore", headers=headers
        )
        return parse_workdrive_response(payload)

    async def delete(
        self,
        *,
        file_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "DELETE", f"/api/v1/files/{file_id}", headers=headers
        )
        return parse_workdrive_response(payload)
