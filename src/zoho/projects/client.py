"""Zoho Projects product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.projects.portals import ProjectsPortalsClient
    from zoho.projects.projects import ProjectsProjectsClient
    from zoho.projects.tasks import ProjectsTasksClient


class ProjectsRequestCallable(Protocol):
    async def __call__(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]: ...


class ProjectsClient:
    """Product-scoped Projects client (V3 endpoints).

    Example:
        ```python
        projects = await zoho.projects.projects.list(portal_id="12345678")
        print(projects[0].id if projects else None)
        ```
    """

    def __init__(
        self, *, request: ProjectsRequestCallable, default_portal_id: str | None = None
    ) -> None:
        self._request_fn = request
        self._default_portal_id = default_portal_id
        self._portals: ProjectsPortalsClient | None = None
        self._projects: ProjectsProjectsClient | None = None
        self._tasks: ProjectsTasksClient | None = None

    @property
    def portals(self) -> ProjectsPortalsClient:
        if self._portals is None:
            from zoho.projects.portals import ProjectsPortalsClient

            self._portals = ProjectsPortalsClient(self)
        return self._portals

    @property
    def projects(self) -> ProjectsProjectsClient:
        if self._projects is None:
            from zoho.projects.projects import ProjectsProjectsClient

            self._projects = ProjectsProjectsClient(self)
        return self._projects

    @property
    def tasks(self) -> ProjectsTasksClient:
        if self._tasks is None:
            from zoho.projects.tasks import ProjectsTasksClient

            self._tasks = ProjectsTasksClient(self)
        return self._tasks

    def resolve_portal_id(self, portal_id: str | int | None) -> str:
        resolved = str(portal_id) if portal_id is not None else self._default_portal_id
        if resolved is None or not str(resolved).strip():
            raise ValueError(
                "portal_id is required (pass explicitly or configure projects_default_portal_id)"
            )
        return str(resolved)

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return await self._request_fn(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
