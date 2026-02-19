"""Projects project operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.projects.models import Project, ProjectsResponse, parse_projects_response

if TYPE_CHECKING:
    from zoho.projects.client import ProjectsClient


class ProjectsProjectsClient:
    """Project resource operations under a portal.

    Example:
        ```python
        created = await zoho.projects.projects.create(
            portal_id="12345678",
            data={"name": "SDK Rollout"},
        )
        print(created.status)
        ```
    """

    def __init__(self, projects_client: ProjectsClient) -> None:
        self._projects = projects_client

    async def list(
        self,
        *,
        portal_id: str | int | None = None,
        page: int = 1,
        per_page: int = 200,
    ) -> list[Project]:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "GET",
            f"/portal/{resolved}/projects",
            params={"page": page, "per_page": per_page},
        )
        return parse_projects_response(payload).projects

    async def get(
        self, *, project_id: str | int, portal_id: str | int | None = None
    ) -> Project | None:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request("GET", f"/portal/{resolved}/projects/{project_id}")
        response = parse_projects_response(payload)

        if response.project is not None:
            return response.project
        if response.projects:
            return response.projects[0]
        return None

    async def create(
        self,
        *,
        data: Mapping[str, Any],
        portal_id: str | int | None = None,
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "POST",
            f"/portal/{resolved}/projects",
            json=dict(data),
        )
        return parse_projects_response(payload)

    async def update(
        self,
        *,
        project_id: str | int,
        data: Mapping[str, Any],
        portal_id: str | int | None = None,
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "PATCH",
            f"/portal/{resolved}/projects/{project_id}",
            json=dict(data),
        )
        return parse_projects_response(payload)

    async def trash(
        self, *, project_id: str | int, portal_id: str | int | None = None
    ) -> ProjectsResponse:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request(
            "POST", f"/portal/{resolved}/projects/{project_id}/trash"
        )
        return parse_projects_response(payload)
