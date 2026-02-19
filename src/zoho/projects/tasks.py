"""Projects task operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.projects.models import ProjectsResponse, Task, parse_projects_response

if TYPE_CHECKING:
    from zoho.projects.client import ProjectsClient


class ProjectsTasksClient:
    """Task resource operations under a project.

    Example:
        ```python
        tasks = await zoho.projects.tasks.list(
            portal_id="12345678",
            project_id="4000000070029",
        )
        print(tasks[0].name if tasks else None)
        ```
    """

    def __init__(self, projects_client: ProjectsClient) -> None:
        self._projects = projects_client

    async def list(
        self,
        *,
        project_id: str | int,
        portal_id: str | int | None = None,
        page: int = 1,
        per_page: int = 200,
    ) -> list[Task]:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "GET",
            f"/portal/{resolved}/projects/{project_id}/tasks",
            params={"page": page, "per_page": per_page},
        )
        return parse_projects_response(payload).tasks

    async def get(
        self,
        *,
        project_id: str | int,
        task_id: str | int,
        portal_id: str | int | None = None,
    ) -> Task | None:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "GET",
            f"/portal/{resolved}/projects/{project_id}/tasks/{task_id}",
        )
        response = parse_projects_response(payload)

        if response.task is not None:
            return response.task
        if response.tasks:
            return response.tasks[0]
        return None

    async def create(
        self,
        *,
        project_id: str | int,
        data: Mapping[str, Any],
        portal_id: str | int | None = None,
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "POST",
            f"/portal/{resolved}/projects/{project_id}/tasks",
            json=dict(data),
        )
        return parse_projects_response(payload)

    async def update(
        self,
        *,
        project_id: str | int,
        task_id: str | int,
        data: Mapping[str, Any],
        portal_id: str | int | None = None,
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "PATCH",
            f"/portal/{resolved}/projects/{project_id}/tasks/{task_id}",
            json=dict(data),
        )
        return parse_projects_response(payload)

    async def close(
        self,
        *,
        project_id: str | int,
        task_id: str | int,
        portal_id: str | int | None = None,
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "POST",
            f"/portal/{resolved}/projects/{project_id}/tasks/{task_id}/close",
        )
        return parse_projects_response(payload)
