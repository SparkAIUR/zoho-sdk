"""Writer document APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.writer.models import WriterResponse, parse_writer_response

if TYPE_CHECKING:
    from zoho.writer.client import WriterClient


class WriterDocumentsClient:
    """Document operations for Zoho Writer."""

    def __init__(self, writer_client: WriterClient) -> None:
        self._writer = writer_client

    async def list(
        self,
        *,
        folder_id: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        search: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        params: dict[str, Any] = {}
        if folder_id:
            params["folder_id"] = folder_id
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search:
            params["search"] = search

        payload = await self._writer.request("GET", "/documents", params=params, headers=headers)
        return parse_writer_response(payload)

    async def get(
        self,
        *,
        document_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request("GET", f"/documents/{document_id}", headers=headers)
        return parse_writer_response(payload)

    async def create(
        self,
        *,
        title: str,
        content: str | None = None,
        folder_id: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        data: dict[str, Any] = {"title": title}
        if content is not None:
            data["content"] = content
        if folder_id is not None:
            data["folder_id"] = folder_id

        payload = await self._writer.request("POST", "/documents", json=data, headers=headers)
        return parse_writer_response(payload)

    async def update(
        self,
        *,
        document_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "PUT",
            f"/documents/{document_id}",
            json=dict(data),
            headers=headers,
        )
        return parse_writer_response(payload)

    async def delete(
        self,
        *,
        document_id: str,
        permanent: bool = False,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "DELETE",
            f"/documents/{document_id}",
            params={"permanent": permanent},
            headers=headers,
        )
        return parse_writer_response(payload)

    async def restore(
        self,
        *,
        document_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "POST",
            f"/documents/{document_id}/restore",
            headers=headers,
        )
        return parse_writer_response(payload)

    async def download(
        self,
        *,
        document_id: str,
        output_format: str = "docx",
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "GET",
            f"/documents/{document_id}/export",
            params={"format": output_format},
            headers=headers,
        )
        return parse_writer_response(payload)
