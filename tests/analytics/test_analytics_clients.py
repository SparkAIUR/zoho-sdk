from __future__ import annotations

from typing import Any

from zoho.analytics.client import AnalyticsClient
from zoho.analytics.models import AnalyticsResponse


class DummyAnalyticsRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"status": "success", "data": [{"id": "a1", "name": "Item 1"}]}


async def test_analytics_metadata_data_bulk_paths() -> None:
    request = DummyAnalyticsRequest()
    analytics = AnalyticsClient(request=request)

    orgs = await analytics.metadata.list_organizations()
    await analytics.data.list_rows(
        workspace_id="workspace_1",
        view_id="view_1",
        config={"limit": 200, "offset": 0},
    )
    await analytics.data.create_rows(
        workspace_id="workspace_1",
        view_id="view_1",
        config={"rows": [{"Email": "alex@example.com"}]},
    )
    await analytics.bulk.get_import_job(workspace_id="workspace_1", job_id="job_1")

    assert isinstance(orgs, AnalyticsResponse)
    assert orgs.result_rows

    paths = [call["path"] for call in request.calls]
    assert "/orgs" in paths
    assert "/workspaces/workspace_1/views/view_1/rows" in paths
    assert "/bulk/workspaces/workspace_1/importjobs/job_1" in paths

    list_call = next(
        call
        for call in request.calls
        if call["path"] == "/workspaces/workspace_1/views/view_1/rows" and call["method"] == "GET"
    )
    assert "CONFIG" in list_call["params"]

    create_call = next(
        call
        for call in request.calls
        if call["path"] == "/workspaces/workspace_1/views/view_1/rows" and call["method"] == "POST"
    )
    assert "CONFIG" in create_call["params"]
