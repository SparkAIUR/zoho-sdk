"""WorkDrive search APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.workdrive.models import WorkDriveResponse, parse_workdrive_response

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient


class WorkDriveSearchClient:
    """Search operations for Zoho WorkDrive."""

    def __init__(self, workdrive_client: WorkDriveClient) -> None:
        self._workdrive = workdrive_client

    async def query(
        self,
        *,
        term: str,
        folder_id: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WorkDriveResponse:
        params: dict[str, Any] = {"search[query]": term}
        if folder_id is not None:
            params["search[parent_id]"] = folder_id
        if offset is not None:
            params["page[offset]"] = offset
        if limit is not None:
            params["page[limit]"] = limit

        payload = await self._workdrive.request(
            "GET",
            "/api/v1/search",
            params=params,
            headers=headers,
        )
        return parse_workdrive_response(payload)
