"""Ingestion iterator helpers for Zoho Analytics."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Mapping
from datetime import datetime
from typing import Any, Literal

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


def _extract_list(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in (
            "rows",
            "data",
            "records",
            "result",
            "items",
            "orgs",
            "workspaces",
            "views",
            "dashboards",
        ):
            value = data.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _extract_updated_at(row: Mapping[str, Any]) -> str | None:
    for key in ("modified_time", "modifiedTime", "updated_at", "updatedAt", "created_time"):
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value:
            return value
        if isinstance(value, (int, float)):
            return str(int(value))
    return None


def _to_epoch_millis(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        try:
            normalized = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            return int(dt.timestamp() * 1000)
        except ValueError:
            return None
    return None


def _extract_high_watermark(row: Mapping[str, Any]) -> int | None:
    for key in ("modified_time", "modifiedTime", "updated_at", "updatedAt", "created_time"):
        parsed = _to_epoch_millis(row.get(key))
        if parsed is not None:
            return parsed
    return None


def _extract_job_id(payload: Mapping[str, Any]) -> str | None:
    data = payload.get("data")
    candidates: list[Any] = [
        payload.get("job_id"),
        payload.get("jobId"),
        payload.get("export_job_id"),
    ]
    if isinstance(data, Mapping):
        candidates.extend(
            [
                data.get("job_id"),
                data.get("jobId"),
                data.get("export_job_id"),
                data.get("exportJobId"),
                data.get("id"),
            ]
        )
    for candidate in candidates:
        if candidate is not None:
            return str(candidate)
    return None


def _extract_job_status(payload: Mapping[str, Any]) -> str | None:
    data = payload.get("data")
    candidates: list[Any] = [payload.get("status"), payload.get("job_status")]
    if isinstance(data, Mapping):
        candidates.extend([data.get("status"), data.get("job_status"), data.get("jobStatus")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate:
            return candidate.lower()
    return None


def _extract_rows_from_response(response: Any) -> list[dict[str, Any]]:
    result_rows = response.result_rows
    if result_rows:
        return [dict(row) for row in result_rows]

    payload = response.model_dump(mode="python")
    rows = _extract_list(payload.get("data"))
    if rows:
        return rows

    return _extract_list(payload)


def _build_analytics_document(
    *,
    row: Mapping[str, Any],
    fallback_id: str,
    source: str,
    entity: str,
    include_content: bool,
    include_raw: bool,
    metadata: Mapping[str, Any] | None = None,
) -> IngestionDocument:
    row_id = row.get("id") or row.get("row_id") or row.get("rowId") or fallback_id
    title = (
        row.get("name")
        or row.get("title")
        or row.get("workspaceName")
        or row.get("viewName")
        or row.get("orgName")
        or row_id
    )

    content: str | None = None
    if include_content:
        for key in ("summary", "description", "display_name", "name"):
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                content = value
                break

    row_metadata: dict[str, Any] = {"entity": entity}
    if metadata:
        row_metadata.update(dict(metadata))

    return IngestionDocument(
        id=str(row_id),
        source=source,
        title=str(title),
        content=content,
        updated_at=_extract_updated_at(row),
        metadata=row_metadata,
        raw=dict(row) if include_raw else {},
    )


async def iter_analytics_workspace_documents(
    client: Zoho,
    *,
    connection_name: str = "default",
    checkpoint: IngestionCheckpoint | None = None,
    include_views: bool = True,
    include_content: bool = False,
    include_raw: bool = False,
    headers: Mapping[str, str] | None = None,
    max_workspaces: int | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield organization/workspace/view metadata documents for indexing."""

    target = resolve_connection(client, connection_name)
    start_offset = checkpoint.offset if checkpoint and checkpoint.offset is not None else 0

    org_response = await target.analytics.metadata.list_organizations(headers=headers)
    workspace_response = await target.analytics.metadata.list_workspaces(headers=headers)

    org_rows = org_response.result_rows
    workspace_rows = workspace_response.result_rows

    if start_offset == 0 and org_rows:
        org_docs = [
            _build_analytics_document(
                row=row,
                fallback_id=f"org:{index}",
                source="zoho.analytics.org",
                entity="org",
                include_content=include_content,
                include_raw=include_raw,
            )
            for index, row in enumerate(org_rows)
        ]
        if org_docs:
            yield IngestionBatch(
                source="zoho.analytics.org",
                documents=org_docs,
                checkpoint=IngestionCheckpoint(
                    offset=0,
                    extras={"entity": "workspace", "phase": "workspaces"},
                )
                if workspace_rows
                else None,
            )

    if start_offset >= len(workspace_rows):
        return

    for processed, workspace_index in enumerate(
        range(start_offset, len(workspace_rows)),
        start=1,
    ):
        workspace_row = workspace_rows[workspace_index]
        workspace_id = (
            workspace_row.get("workspaceId")
            or workspace_row.get("workspace_id")
            or workspace_row.get("id")
            or f"workspace:{workspace_index}"
        )

        docs = [
            _build_analytics_document(
                row=workspace_row,
                fallback_id=f"workspace:{workspace_index}",
                source="zoho.analytics.workspace",
                entity="workspace",
                include_content=include_content,
                include_raw=include_raw,
            )
        ]

        if include_views:
            view_response = await target.analytics.metadata.list_views(
                workspace_id=str(workspace_id),
                headers=headers,
            )
            for view_index, view_row in enumerate(view_response.result_rows):
                docs.append(
                    _build_analytics_document(
                        row=view_row,
                        fallback_id=f"{workspace_id}:view:{view_index}",
                        source="zoho.analytics.view",
                        entity="view",
                        include_content=include_content,
                        include_raw=include_raw,
                        metadata={"workspace_id": str(workspace_id)},
                    )
                )

        next_offset = workspace_index + 1
        yield IngestionBatch(
            source="zoho.analytics.workspace",
            documents=docs,
            checkpoint=(
                IngestionCheckpoint(
                    offset=next_offset,
                    extras={
                        "entity": "workspace",
                        "include_views": include_views,
                    },
                )
                if next_offset < len(workspace_rows)
                else None
            ),
        )

        if max_workspaces is not None and processed >= max_workspaces:
            break


async def iter_analytics_view_documents(
    client: Zoho,
    *,
    workspace_id: str,
    view_id: str,
    strategy: Literal["bulk", "direct"] = "bulk",
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
    config: Mapping[str, Any] | None = None,
    max_poll_attempts: int = 10,
    poll_interval_seconds: float = 1.0,
    include_content: bool = False,
    include_raw: bool = False,
    headers: Mapping[str, str] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield view row documents using either direct or bulk strategy."""

    target = resolve_connection(client, connection_name)

    if strategy == "direct":
        offset = checkpoint.offset if checkpoint and checkpoint.offset is not None else 0
        high_watermark = _to_epoch_millis(checkpoint.updated_at) if checkpoint else None

        pages = 0
        while True:
            request_config = dict(config or {})
            request_config.setdefault("limit", page_size)
            request_config.setdefault("offset", offset)

            response = await target.analytics.data.list_rows(
                workspace_id=workspace_id,
                view_id=view_id,
                config=request_config,
                headers=headers,
            )
            rows = _extract_rows_from_response(response)
            if not rows:
                break

            docs: list[IngestionDocument] = []
            for row_index, row in enumerate(rows):
                docs.append(
                    _build_analytics_document(
                        row=row,
                        fallback_id=f"{view_id}:{offset}:{row_index}",
                        source="zoho.analytics.row",
                        entity="view_row",
                        include_content=include_content,
                        include_raw=include_raw,
                        metadata={
                            "workspace_id": workspace_id,
                            "view_id": view_id,
                            "strategy": "direct",
                        },
                    )
                )
                row_watermark = _extract_high_watermark(row)
                if row_watermark is not None and (
                    high_watermark is None or row_watermark > high_watermark
                ):
                    high_watermark = row_watermark

            next_offset = offset + len(rows)
            yield IngestionBatch(
                source="zoho.analytics.row",
                documents=docs,
                checkpoint=IngestionCheckpoint(
                    offset=next_offset,
                    updated_at=str(high_watermark) if high_watermark is not None else None,
                    extras={
                        "workspace_id": workspace_id,
                        "view_id": view_id,
                        "strategy": "direct",
                    },
                ),
            )

            pages += 1
            if max_pages is not None and pages >= max_pages:
                break
            if len(rows) < page_size:
                break
            offset = next_offset

        return

    if strategy != "bulk":
        raise ValueError(f"Unsupported analytics ingestion strategy: {strategy}")

    request_config = dict(config or {})
    job_id = checkpoint.cursor if checkpoint and checkpoint.cursor else None
    if job_id is None:
        export_response = await target.analytics.bulk.export_data(
            workspace_id=workspace_id,
            view_id=view_id,
            config=request_config,
            headers=headers,
        )

        direct_rows = _extract_rows_from_response(export_response)
        if direct_rows:
            docs = [
                _build_analytics_document(
                    row=row,
                    fallback_id=f"{view_id}:bulk:{index}",
                    source="zoho.analytics.row",
                    entity="view_row",
                    include_content=include_content,
                    include_raw=include_raw,
                    metadata={
                        "workspace_id": workspace_id,
                        "view_id": view_id,
                        "strategy": "bulk",
                    },
                )
                for index, row in enumerate(direct_rows)
            ]
            yield IngestionBatch(source="zoho.analytics.row", documents=docs, checkpoint=None)
            return

        export_payload = export_response.model_dump(mode="python")
        job_id = _extract_job_id(export_payload)
        if job_id is None:
            yield IngestionBatch(source="zoho.analytics.row", documents=[], checkpoint=None)
            return

    status: str | None = None
    for _ in range(max_poll_attempts):
        poll_response = await target.analytics.bulk.get_export_job(
            workspace_id=workspace_id,
            job_id=job_id,
            headers=headers,
        )
        poll_payload = poll_response.model_dump(mode="python")
        status = _extract_job_status(poll_payload)
        if status in {"success", "complete", "completed", "ready", "finished"}:
            break
        if status in {"failed", "failure", "error", "cancelled", "canceled"}:
            raise RuntimeError(f"Analytics export job {job_id} failed with status={status}")
        if poll_interval_seconds > 0:
            await asyncio.sleep(poll_interval_seconds)
    else:
        yield IngestionBatch(
            source="zoho.analytics.row",
            documents=[],
            checkpoint=IngestionCheckpoint(
                cursor=job_id,
                extras={
                    "workspace_id": workspace_id,
                    "view_id": view_id,
                    "strategy": "bulk",
                    "status": status,
                },
            ),
        )
        return

    download_response = await target.analytics.bulk.download_export_job(
        workspace_id=workspace_id,
        job_id=job_id,
        headers=headers,
    )
    rows = _extract_rows_from_response(download_response)
    docs = [
        _build_analytics_document(
            row=row,
            fallback_id=f"{view_id}:bulk:{index}",
            source="zoho.analytics.row",
            entity="view_row",
            include_content=include_content,
            include_raw=include_raw,
            metadata={
                "workspace_id": workspace_id,
                "view_id": view_id,
                "strategy": "bulk",
                "job_id": job_id,
            },
        )
        for index, row in enumerate(rows)
    ]

    yield IngestionBatch(source="zoho.analytics.row", documents=docs, checkpoint=None)
