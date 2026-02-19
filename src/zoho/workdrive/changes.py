"""WorkDrive recent changes APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.workdrive.models import WorkDriveResponse, parse_workdrive_response

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient


class WorkDriveChangesClient:
    """Delta and recent-change operations for ingestion connectors."""

    def __init__(self, workdrive_client: WorkDriveClient) -> None:
        self._workdrive = workdrive_client

    async def list_recent(
        self,
        *,
        folder_id: str,
        cursor: str | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        params: dict[str, Any] = {}
        if cursor is not None:
            params["page[next]"] = cursor
        if limit is not None:
            params["page[limit]"] = limit

        payload = await self._workdrive.request(
            "GET",
            f"/api/v1/files/{folder_id}/recentchanges",
            params=params,
            headers=headers,
        )
        return parse_workdrive_response(payload)
