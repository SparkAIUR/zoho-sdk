"""Zoho Writer product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.writer.documents import WriterDocumentsClient
    from zoho.writer.folders import WriterFoldersClient
    from zoho.writer.merge import WriterMergeClient


class WriterRequestCallable(Protocol):
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


class WriterClient:
    """Product-scoped Writer client."""

    def __init__(self, *, request: WriterRequestCallable) -> None:
        self._request_fn = request
        self._documents: WriterDocumentsClient | None = None
        self._folders: WriterFoldersClient | None = None
        self._merge: WriterMergeClient | None = None

    @property
    def documents(self) -> WriterDocumentsClient:
        if self._documents is None:
            from zoho.writer.documents import WriterDocumentsClient

            self._documents = WriterDocumentsClient(self)
        return self._documents

    @property
    def folders(self) -> WriterFoldersClient:
        if self._folders is None:
            from zoho.writer.folders import WriterFoldersClient

            self._folders = WriterFoldersClient(self)
        return self._folders

    @property
    def merge(self) -> WriterMergeClient:
        if self._merge is None:
            from zoho.writer.merge import WriterMergeClient

            self._merge = WriterMergeClient(self)
        return self._merge

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
