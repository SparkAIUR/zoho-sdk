"""Projects portal operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from zoho.projects.models import Portal, parse_projects_response

if TYPE_CHECKING:
    from zoho.projects.client import ProjectsClient


class ProjectsPortalsClient:
    """Portal-level operations."""

    def __init__(self, projects_client: ProjectsClient) -> None:
        self._projects = projects_client

    async def list(self) -> list[Portal]:
        payload = await self._projects.request("GET", "/portal")
        return parse_projects_response(payload).portals

    async def get(self, *, portal_id: str | int | None = None) -> Portal | None:
        resolved = self._projects.resolve_portal_id(portal_id)
        payload = await self._projects.request("GET", f"/portal/{resolved}")
        response = parse_projects_response(payload)

        if response.portal is not None:
            return response.portal
        if response.portals:
            return response.portals[0]
        return None
