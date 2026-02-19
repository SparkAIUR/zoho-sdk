from __future__ import annotations

from typing import Any

import pytest

from zoho.projects.client import ProjectsClient
from zoho.projects.models import Portal, Project, Task


class DummyProjectsRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})

        if path == "/portal":
            return {"portals": [{"id": "100"}]}
        if path.endswith("/projects"):
            return {"projects": [{"id": "200"}]}
        if "/tasks" in path:
            return {"tasks": [{"id": "300"}]}
        return {"project": {"id": "200"}}


async def test_projects_clients_use_portal_scoped_paths() -> None:
    request = DummyProjectsRequest()
    projects = ProjectsClient(request=request, default_portal_id="100")

    portals = await projects.portals.list()
    project_rows = await projects.projects.list()
    task_rows = await projects.tasks.list(project_id="200")

    assert isinstance(portals[0], Portal)
    assert isinstance(project_rows[0], Project)
    assert isinstance(task_rows[0], Task)
    assert portals[0].id == "100"
    assert project_rows[0].id == "200"
    assert task_rows[0].id == "300"

    called_paths = [call["path"] for call in request.calls]
    assert "/portal" in called_paths
    assert "/portal/100/projects" in called_paths
    assert "/portal/100/projects/200/tasks" in called_paths


def test_projects_requires_portal_id() -> None:
    projects = ProjectsClient(request=DummyProjectsRequest(), default_portal_id=None)

    with pytest.raises(ValueError):
        projects.resolve_portal_id(None)
