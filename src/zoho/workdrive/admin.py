"""WorkDrive admin APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from zoho.workdrive.models import WorkDriveResponse, parse_workdrive_response

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient


class WorkDriveAdminClient:
    """Team and admin operations for Zoho WorkDrive."""

    def __init__(self, workdrive_client: WorkDriveClient) -> None:
        self._workdrive = workdrive_client

    async def list_teams(self, *, headers: Mapping[str, str] | None = None) -> WorkDriveResponse:
        payload = await self._workdrive.request("GET", "/api/v1/teams", headers=headers)
        return parse_workdrive_response(payload)

    async def list_team_members(
        self,
        *,
        team_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "GET",
            f"/api/v1/teams/{team_id}/members",
            headers=headers,
        )
        return parse_workdrive_response(payload)

    async def list_team_folders(
        self,
        *,
        team_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        payload = await self._workdrive.request(
            "GET",
            f"/api/v1/teams/{team_id}/teamfolders",
            headers=headers,
        )
        return parse_workdrive_response(payload)
