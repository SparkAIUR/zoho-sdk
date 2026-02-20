"""Writer merge APIs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.writer.models import WriterResponse, parse_writer_response

if TYPE_CHECKING:
    from zoho.writer.client import WriterClient


class WriterMergeClient:
    """Merge and automation APIs for Zoho Writer."""

    def __init__(self, writer_client: WriterClient) -> None:
        self._writer = writer_client

    async def get_fields(
        self,
        *,
        document_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "GET",
            f"/documents/{document_id}/fields",
            headers=headers,
        )
        return parse_writer_response(payload)

    async def merge_and_download(
        self,
        *,
        document_id: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        output_format: str = "pdf",
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        payload = await self._writer.request(
            "POST",
            f"/documents/{document_id}/merge/download",
            json={"data": data, "output_format": output_format},
            headers=headers,
        )
        return parse_writer_response(payload)

    async def merge_and_store(
        self,
        *,
        document_id: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        folder_id: str | None = None,
        output_format: str = "pdf",
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        body: dict[str, Any] = {"data": data, "output_format": output_format}
        if folder_id is not None:
            body["folder_id"] = folder_id

        payload = await self._writer.request(
            "POST",
            f"/documents/{document_id}/merge/store",
            json=body,
            headers=headers,
        )
        return parse_writer_response(payload)

    async def merge_and_send(
        self,
        *,
        document_id: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        email_to: Sequence[str],
        subject: str | None = None,
        message: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> WriterResponse:
        body: dict[str, Any] = {
            "data": data,
            "to": list(email_to),
        }
        if subject is not None:
            body["subject"] = subject
        if message is not None:
            body["message"] = message

        payload = await self._writer.request(
            "POST",
            f"/documents/{document_id}/merge/email",
            json=body,
            headers=headers,
        )
        return parse_writer_response(payload)
