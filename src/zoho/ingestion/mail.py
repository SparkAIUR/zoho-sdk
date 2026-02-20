"""Ingestion iterator helpers for Zoho Mail."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import Any

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


def _extract_mail_updated_at(row: Mapping[str, Any]) -> str | None:
    for key in ("receivedTime", "sentDateInGMT", "receivedDateInGMT", "modifiedTime"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, (int, float)):
            return str(value)
    return None


async def iter_mail_message_documents(
    client: Zoho,
    *,
    account_id: str | int,
    folder_id: str | int | None = None,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
    extra_params: Mapping[str, Any] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from Zoho Mail message lists."""

    target = resolve_connection(client, connection_name)
    start = checkpoint.offset if checkpoint and checkpoint.offset is not None else 1

    pages = 0
    while True:
        response = await target.mail.messages.list(
            account_id=account_id,
            folder_id=folder_id,
            start=start,
            limit=page_size,
            extra_params=extra_params,
        )
        rows = response.result_rows
        if not rows:
            break

        docs: list[IngestionDocument] = []
        for index, row in enumerate(rows):
            rid = row.get("messageId") or row.get("id") or f"{account_id}:{start}:{index}"
            docs.append(
                IngestionDocument(
                    id=str(rid),
                    source="zoho.mail",
                    title=str(row.get("subject") or row.get("threadSubject") or rid),
                    content=(
                        str(row.get("summary") or row.get("content") or row.get("snippet") or "")
                        or None
                    ),
                    updated_at=_extract_mail_updated_at(row),
                    metadata={
                        "account_id": str(account_id),
                        "folder_id": str(folder_id) if folder_id is not None else None,
                        "start": start,
                    },
                    raw=dict(row),
                )
            )

        next_start = start + len(rows)
        yield IngestionBatch(
            source="zoho.mail",
            documents=docs,
            checkpoint=IngestionCheckpoint(
                offset=next_start,
                extras={
                    "account_id": str(account_id),
                    "folder_id": str(folder_id) if folder_id is not None else None,
                },
            ),
        )

        pages += 1
        if len(rows) < page_size:
            break
        if max_pages is not None and pages >= max_pages:
            break
        start = next_start
