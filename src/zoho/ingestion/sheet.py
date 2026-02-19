"""Ingestion iterator helpers for Zoho Sheet."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


def _extract_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("records")
    if isinstance(rows, list):
        return [item for item in rows if isinstance(item, dict)]

    data = payload.get("data")
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    return []


async def iter_sheet_worksheet_documents(
    client: Zoho,
    *,
    workbook_id: str,
    worksheet_name: str,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from Sheet worksheet records."""

    target = resolve_connection(client, connection_name)
    offset = checkpoint.offset if checkpoint and checkpoint.offset is not None else 0

    pages = 0
    while True:
        response = await target.sheet.tabular.fetch_worksheet_records(
            workbook_id=workbook_id,
            worksheet_name=worksheet_name,
            offset=offset,
            limit=page_size,
        )
        rows = _extract_rows(response.model_dump(mode="python"))
        if not rows:
            break

        docs: list[IngestionDocument] = []
        for row in rows:
            rid = row.get("id") or row.get("row_id") or f"{worksheet_name}:{offset}:{len(docs)}"
            docs.append(
                IngestionDocument(
                    id=str(rid),
                    source="zoho.sheet",
                    title=str(row.get("title") or row.get("name") or rid),
                    content=str(row.get("content") or row.get("value") or "") or None,
                    updated_at=(
                        str(row.get("modified_time") or row.get("updated_at"))
                        if row.get("modified_time") or row.get("updated_at")
                        else None
                    ),
                    metadata={"workbook_id": workbook_id, "worksheet_name": worksheet_name},
                    raw=row,
                )
            )

        next_offset = offset + len(rows)
        yield IngestionBatch(
            source="zoho.sheet",
            documents=docs,
            checkpoint=IngestionCheckpoint(
                offset=next_offset,
                extras={"workbook_id": workbook_id, "worksheet_name": worksheet_name},
            ),
        )

        pages += 1
        if len(rows) < page_size:
            break
        if max_pages is not None and pages >= max_pages:
            break
        offset = next_offset
