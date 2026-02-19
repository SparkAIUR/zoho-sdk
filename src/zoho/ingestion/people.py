"""Ingestion iterator helpers for Zoho People."""

from __future__ import annotations

from collections.abc import AsyncIterator

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


async def iter_people_form_documents(
    client: Zoho,
    *,
    form_link_name: str,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from People form records."""

    target = resolve_connection(client, connection_name)
    start_index = checkpoint.offset if checkpoint and checkpoint.offset is not None else 0

    pages = 0
    while True:
        response = await target.people.forms.list_records(
            form_link_name=form_link_name,
            from_index=start_index,
            limit=page_size,
        )
        rows = response.result_rows
        if not rows:
            break

        docs: list[IngestionDocument] = []
        for row in rows:
            rid = (
                row.get("recordId")
                or row.get("record_id")
                or row.get("id")
                or row.get("employeeId")
                or row.get("zoho_id")
                or f"{form_link_name}:{start_index}:{len(docs)}"
            )
            docs.append(
                IngestionDocument(
                    id=str(rid),
                    source="zoho.people",
                    title=str(row.get("displayName") or row.get("name") or rid),
                    content=str(row.get("description") or "") or None,
                    updated_at=(
                        str(row.get("modifiedTime") or row.get("modified_time"))
                        if row.get("modifiedTime") or row.get("modified_time")
                        else None
                    ),
                    metadata={"form_link_name": form_link_name},
                    raw=row,
                )
            )

        next_offset = start_index + len(rows)
        yield IngestionBatch(
            source="zoho.people",
            documents=docs,
            checkpoint=IngestionCheckpoint(
                offset=next_offset, extras={"form_link_name": form_link_name}
            ),
        )

        pages += 1
        if len(rows) < page_size:
            break
        if max_pages is not None and pages >= max_pages:
            break
        start_index = next_offset
