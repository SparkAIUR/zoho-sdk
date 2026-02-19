"""Ingestion iterator helpers for Zoho CRM."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from typing import Any

from zoho.client import Zoho
from zoho.crm.models import RecordListResponse
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


def _extract_updated_at(row: Mapping[str, Any]) -> str | None:
    for key in ("Modified_Time", "modified_time", "Updated_Time", "updated_at"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _extract_title(module: str, row: Mapping[str, Any], fallback_id: str) -> str:
    for key in ("Full_Name", "Last_Name", "Name", "Subject", "Company"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return f"{module}:{fallback_id}"


def _extract_content(row: Mapping[str, Any]) -> str | None:
    for key in ("Description", "description"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _next_page_from_response(
    response: RecordListResponse, *, page: int, page_size: int
) -> int | None:
    if response.info is not None and response.info.more_records:
        if response.info.page is not None:
            return response.info.page + 1
        return page + 1
    if len(response.data) == page_size:
        return page + 1
    return None


def _build_module_checkpoint(
    *,
    next_page: int,
    module: str,
    fields: Sequence[str] | None,
) -> IngestionCheckpoint:
    extras: dict[str, Any] = {"module": module}
    if fields:
        extras["fields"] = list(fields)
    return IngestionCheckpoint(page=next_page, extras=extras)


async def iter_crm_module_documents(
    client: Zoho,
    *,
    module: str,
    fields: Sequence[str] | None = None,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
    extra_params: Mapping[str, Any] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches from one CRM module."""

    target = resolve_connection(client, connection_name)
    page = checkpoint.page if checkpoint and checkpoint.page is not None else 1

    pages = 0
    while True:
        response = await target.crm.records.list(
            module=module,
            page=page,
            per_page=page_size,
            fields=fields,
            extra_params=extra_params,
        )
        rows = response.data
        if not rows:
            break

        docs: list[IngestionDocument] = []
        for index, row in enumerate(rows):
            rid = row.get("id")
            doc_id = str(rid) if rid is not None else f"{module}:{page}:{index}"
            docs.append(
                IngestionDocument(
                    id=doc_id,
                    source="zoho.crm",
                    title=_extract_title(module, row, doc_id),
                    content=_extract_content(row),
                    updated_at=_extract_updated_at(row),
                    metadata={"module": module, "page": page},
                    raw=dict(row),
                )
            )

        next_page = _next_page_from_response(response, page=page, page_size=page_size)
        yield IngestionBatch(
            source="zoho.crm",
            documents=docs,
            checkpoint=(
                _build_module_checkpoint(next_page=next_page, module=module, fields=fields)
                if next_page is not None
                else None
            ),
        )

        pages += 1
        if max_pages is not None and pages >= max_pages:
            break
        if next_page is None:
            break
        page = next_page


def _normalize_module_index(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return 0


async def iter_crm_documents(
    client: Zoho,
    *,
    modules: Sequence[str],
    fields_by_module: Mapping[str, Sequence[str]] | None = None,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages_per_module: int | None = None,
    extra_params_by_module: Mapping[str, Mapping[str, Any]] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized document batches across an explicit module allowlist."""

    if not modules:
        raise ValueError("modules must contain at least one CRM module API name")

    start_module_index = (
        _normalize_module_index(checkpoint.extras.get("module_index"))
        if checkpoint is not None
        else 0
    )
    if start_module_index < 0:
        start_module_index = 0
    if start_module_index >= len(modules):
        return

    for module_index in range(start_module_index, len(modules)):
        module_name = modules[module_index]
        module_fields = fields_by_module.get(module_name) if fields_by_module else None
        module_extra_params = (
            extra_params_by_module.get(module_name) if extra_params_by_module else None
        )
        module_checkpoint = (
            IngestionCheckpoint(page=checkpoint.page, extras=checkpoint.extras)
            if checkpoint is not None and module_index == start_module_index
            else None
        )

        async for batch in iter_crm_module_documents(
            client,
            module=module_name,
            fields=module_fields,
            connection_name=connection_name,
            page_size=page_size,
            checkpoint=module_checkpoint,
            max_pages=max_pages_per_module,
            extra_params=module_extra_params,
        ):
            module_checkpoint = None

            batch_checkpoint = batch.checkpoint
            if batch_checkpoint is None:
                next_checkpoint = None
            else:
                next_checkpoint = IngestionCheckpoint(
                    cursor=batch_checkpoint.cursor,
                    offset=batch_checkpoint.offset,
                    page=batch_checkpoint.page,
                    updated_at=batch_checkpoint.updated_at,
                    extras={
                        **batch_checkpoint.extras,
                        "module_name": module_name,
                        "module_index": module_index,
                    },
                )

            yield IngestionBatch(
                source=batch.source,
                documents=batch.documents,
                checkpoint=next_checkpoint,
            )
