"""Reusable Analytics ingestion workflow skeleton for connector jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from zoho import Zoho
from zoho.ingestion import (
    iter_analytics_view_documents,
    iter_analytics_workspace_documents,
)
from zoho.ingestion.models import IngestionCheckpoint, IngestionDocument


# --8<-- [start:checkpoint_store]
class JsonCheckpointStore:
    """Simple file checkpoint store for demos and local connector runs."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self, job_name: str) -> IngestionCheckpoint | None:
        if not self._path.exists():
            return None
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        checkpoint_payload = payload.get(job_name)
        if not isinstance(checkpoint_payload, dict):
            return None
        return IngestionCheckpoint.model_validate(checkpoint_payload)

    def save(self, job_name: str, checkpoint: IngestionCheckpoint | None) -> None:
        state: dict[str, Any] = {}
        if self._path.exists():
            state = json.loads(self._path.read_text(encoding="utf-8"))
        state[job_name] = checkpoint.model_dump(mode="python") if checkpoint else None
        self._path.write_text(json.dumps(state, indent=2), encoding="utf-8")


# --8<-- [end:checkpoint_store]


# --8<-- [start:index_documents]
async def index_documents(documents: list[IngestionDocument]) -> None:
    """Replace this with your search/index write path."""

    for document in documents:
        print("INDEX", document.source, document.id, document.updated_at)


# --8<-- [end:index_documents]


# --8<-- [start:workspace_graph_job]
async def run_workspace_graph_job(
    client: Zoho,
    checkpoint_store: JsonCheckpointStore,
    *,
    analytics_org_id: str,
) -> None:
    checkpoint = checkpoint_store.load("analytics_workspace_graph")

    async for batch in iter_analytics_workspace_documents(
        client,
        checkpoint=checkpoint,
        include_views=True,
        max_workspaces=25,
        headers={"ZANALYTICS-ORGID": analytics_org_id},
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("analytics_workspace_graph", batch.checkpoint)


# --8<-- [end:workspace_graph_job]


# --8<-- [start:view_rows_job]
async def run_view_rows_job(
    client: Zoho,
    checkpoint_store: JsonCheckpointStore,
    *,
    analytics_org_id: str,
    workspace_id: str,
    view_id: str,
    strategy: Literal["bulk", "direct"] = "bulk",
) -> None:
    checkpoint_key = f"analytics_view_rows:{workspace_id}:{view_id}:{strategy}"
    checkpoint = checkpoint_store.load(checkpoint_key)

    async for batch in iter_analytics_view_documents(
        client,
        workspace_id=workspace_id,
        view_id=view_id,
        strategy=strategy,
        checkpoint=checkpoint,
        page_size=200,
        max_pages=10 if strategy == "direct" else None,
        max_poll_attempts=10,
        poll_interval_seconds=0.5,
        headers={"ZANALYTICS-ORGID": analytics_org_id},
    ):
        await index_documents(batch.documents)
        checkpoint_store.save(checkpoint_key, batch.checkpoint)


# --8<-- [end:view_rows_job]


# --8<-- [start:runner]
async def run_analytics_connector() -> None:
    client = Zoho.from_credentials(
        client_id="${ZOHO_CLIENT_ID}",
        client_secret="${ZOHO_CLIENT_SECRET}",
        refresh_token="${ZOHO_REFRESH_TOKEN}",
    )

    checkpoint_store = JsonCheckpointStore(Path(".checkpoints/zoho-analytics.json"))
    checkpoint_store._path.parent.mkdir(parents=True, exist_ok=True)

    try:
        await run_workspace_graph_job(
            client,
            checkpoint_store,
            analytics_org_id="123456789",
        )
        await run_view_rows_job(
            client,
            checkpoint_store,
            analytics_org_id="123456789",
            workspace_id="workspace_123",
            view_id="view_123",
            strategy="bulk",
        )
    finally:
        await client.close()


# --8<-- [end:runner]
