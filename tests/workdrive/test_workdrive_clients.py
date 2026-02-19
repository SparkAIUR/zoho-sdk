from __future__ import annotations

from typing import Any

from zoho.workdrive.client import WorkDriveClient
from zoho.workdrive.models import WorkDriveResponse


class DummyWorkDriveRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {
            "data": [
                {
                    "id": "wd_1",
                    "type": "files",
                    "attributes": {"name": "File 1"},
                }
            ],
            "links": {"cursor": {"has_next": False}},
        }


async def test_workdrive_changes_and_admin_paths() -> None:
    request = DummyWorkDriveRequest()
    workdrive = WorkDriveClient(request=request)

    changes = await workdrive.changes.list_recent(folder_id="f1", limit=100)
    await workdrive.admin.list_teams()

    assert isinstance(changes, WorkDriveResponse)
    assert changes.resources

    paths = [call["path"] for call in request.calls]
    assert "/api/v1/files/f1/recentchanges" in paths
    assert "/api/v1/teams" in paths
