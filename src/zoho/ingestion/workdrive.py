"""Ingestion iterator helpers for Zoho WorkDrive."""

from __future__ import annotations

from collections.abc import AsyncIterator

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


async def iter_workdrive_recent_documents(
    client: Zoho,
    *,
    folder_id: str,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from WorkDrive recent changes feed."""

    target = resolve_connection(client, connection_name)
    cursor = checkpoint.cursor if checkpoint else None

    pages = 0
    while True:
        response = await target.workdrive.changes.list_recent(
            folder_id=folder_id,
            cursor=cursor,
            limit=page_size,
        )
        resources = response.resources
        if not resources:
            break

        docs: list[IngestionDocument] = []
        for resource in resources:
            attrs = resource.attributes
            rid = resource.id or attrs.get("id") or f"{folder_id}:{len(docs)}"
            docs.append(
                IngestionDocument(
                    id=str(rid),
                    source="zoho.workdrive",
                    title=(
                        str(attrs.get("name") or attrs.get("title") or rid)
                        if attrs.get("name") or attrs.get("title")
                        else str(rid)
                    ),
                    content=str(attrs.get("description") or "") or None,
                    mime_type=(str(attrs.get("mime_type")) if attrs.get("mime_type") else None),
                    url=(str(attrs.get("permalink")) if attrs.get("permalink") else None),
                    updated_at=(
                        str(attrs.get("modified_time") or attrs.get("updated_at"))
                        if attrs.get("modified_time") or attrs.get("updated_at")
                        else None
                    ),
                    metadata={"folder_id": folder_id, "resource_type": resource.type},
                    raw=resource.model_dump(mode="python"),
                )
            )

        links = response.links
        next_cursor_raw = links.get("cursor") if isinstance(links, dict) else None
        next_cursor: str | None = None
        if isinstance(next_cursor_raw, dict):
            token = next_cursor_raw.get("next")
            if isinstance(token, str) and token:
                next_cursor = token

        yield IngestionBatch(
            source="zoho.workdrive",
            documents=docs,
            checkpoint=IngestionCheckpoint(cursor=next_cursor, extras={"folder_id": folder_id}),
        )

        pages += 1
        if max_pages is not None and pages >= max_pages:
            break
        if next_cursor is None:
            break
        cursor = next_cursor
