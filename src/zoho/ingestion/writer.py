"""Ingestion iterator helpers for Zoho Writer."""

from __future__ import annotations

from collections.abc import AsyncIterator

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


async def iter_writer_document_documents(
    client: Zoho,
    *,
    folder_id: str | None = None,
    search: str | None = None,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from Zoho Writer documents."""

    target = resolve_connection(client, connection_name)
    page = checkpoint.page if checkpoint and checkpoint.page is not None else 1

    pages = 0
    while True:
        response = await target.writer.documents.list(
            folder_id=folder_id,
            page=page,
            limit=page_size,
            search=search,
        )
        rows = response.result_rows
        if not rows:
            break

        docs: list[IngestionDocument] = []
        for index, row in enumerate(rows):
            rid = row.get("id") or row.get("document_id") or f"writer:{page}:{index}"
            docs.append(
                IngestionDocument(
                    id=str(rid),
                    source="zoho.writer",
                    title=str(row.get("title") or row.get("name") or rid),
                    content=str(row.get("description") or row.get("snippet") or "") or None,
                    updated_at=(
                        str(
                            row.get("modified_time")
                            or row.get("modifiedTime")
                            or row.get("updated_at")
                        )
                        if row.get("modified_time")
                        or row.get("modifiedTime")
                        or row.get("updated_at")
                        else None
                    ),
                    metadata={
                        "folder_id": folder_id,
                        "search": search,
                        "page": page,
                    },
                    raw=dict(row),
                )
            )

        next_page = page + 1
        yield IngestionBatch(
            source="zoho.writer",
            documents=docs,
            checkpoint=IngestionCheckpoint(
                page=next_page,
                extras={"folder_id": folder_id, "search": search},
            ),
        )

        pages += 1
        if len(rows) < page_size:
            break
        if max_pages is not None and pages >= max_pages:
            break
        page = next_page
