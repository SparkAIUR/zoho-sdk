"""Zoho WorkDrive product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.workdrive.admin import WorkDriveAdminClient
    from zoho.workdrive.changes import WorkDriveChangesClient
    from zoho.workdrive.files import WorkDriveFilesClient
    from zoho.workdrive.folders import WorkDriveFoldersClient
    from zoho.workdrive.search import WorkDriveSearchClient


class WorkDriveRequestCallable(Protocol):
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


class WorkDriveClient:
    """Product-scoped WorkDrive client."""

    def __init__(self, *, request: WorkDriveRequestCallable) -> None:
        self._request_fn = request
        self._files: WorkDriveFilesClient | None = None
        self._folders: WorkDriveFoldersClient | None = None
        self._search: WorkDriveSearchClient | None = None
        self._changes: WorkDriveChangesClient | None = None
        self._admin: WorkDriveAdminClient | None = None

    @property
    def files(self) -> WorkDriveFilesClient:
        if self._files is None:
            from zoho.workdrive.files import WorkDriveFilesClient

            self._files = WorkDriveFilesClient(self)
        return self._files

    @property
    def folders(self) -> WorkDriveFoldersClient:
        if self._folders is None:
            from zoho.workdrive.folders import WorkDriveFoldersClient

            self._folders = WorkDriveFoldersClient(self)
        return self._folders

    @property
    def search(self) -> WorkDriveSearchClient:
        if self._search is None:
            from zoho.workdrive.search import WorkDriveSearchClient

            self._search = WorkDriveSearchClient(self)
        return self._search

    @property
    def changes(self) -> WorkDriveChangesClient:
        if self._changes is None:
            from zoho.workdrive.changes import WorkDriveChangesClient

            self._changes = WorkDriveChangesClient(self)
        return self._changes

    @property
    def admin(self) -> WorkDriveAdminClient:
        if self._admin is None:
            from zoho.workdrive.admin import WorkDriveAdminClient

            self._admin = WorkDriveAdminClient(self)
        return self._admin

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
