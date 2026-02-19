"""Reusable ingestion workflow skeleton for batch connector jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zoho import Zoho
from zoho.ingestion import (
    iter_crm_documents,
    iter_people_form_documents,
    iter_sheet_worksheet_documents,
    iter_workdrive_recent_documents,
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


# --8<-- [start:crm_job]
async def run_crm_job(client: Zoho, checkpoint_store: JsonCheckpointStore) -> None:
    checkpoint = checkpoint_store.load("crm")
    last_checkpoint = checkpoint

    async for batch in iter_crm_documents(
        client,
        modules=["Leads", "Contacts", "Accounts"],
        fields_by_module={
            "Leads": ["id", "Full_Name", "Email", "Modified_Time"],
            "Contacts": ["id", "Full_Name", "Email", "Modified_Time"],
            "Accounts": ["id", "Account_Name", "Modified_Time"],
        },
        page_size=200,
        checkpoint=checkpoint,
        max_pages_per_module=10,
    ):
        await index_documents(batch.documents)
        last_checkpoint = batch.checkpoint
        checkpoint_store.save("crm", last_checkpoint)
# --8<-- [end:crm_job]


# --8<-- [start:multi_source_job]
async def run_multi_source_job(client: Zoho, checkpoint_store: JsonCheckpointStore) -> None:
    people_checkpoint = checkpoint_store.load("people")
    async for batch in iter_people_form_documents(
        client,
        form_link_name="employee",
        checkpoint=people_checkpoint,
        page_size=200,
        max_pages=5,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("people", batch.checkpoint)

    sheet_checkpoint = checkpoint_store.load("sheet")
    async for batch in iter_sheet_worksheet_documents(
        client,
        workbook_id="workbook_123",
        worksheet_name="Directory",
        checkpoint=sheet_checkpoint,
        page_size=500,
        max_pages=5,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("sheet", batch.checkpoint)

    workdrive_checkpoint = checkpoint_store.load("workdrive")
    async for batch in iter_workdrive_recent_documents(
        client,
        folder_id="folder_123",
        checkpoint=workdrive_checkpoint,
        page_size=200,
        max_pages=5,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("workdrive", batch.checkpoint)
# --8<-- [end:multi_source_job]


# --8<-- [start:runner]
async def run_connector() -> None:
    client = Zoho.from_credentials(
        client_id="${ZOHO_CLIENT_ID}",
        client_secret="${ZOHO_CLIENT_SECRET}",
        refresh_token="${ZOHO_REFRESH_TOKEN}",
    )

    checkpoint_store = JsonCheckpointStore(Path(".checkpoints/zoho.json"))
    checkpoint_store._path.parent.mkdir(parents=True, exist_ok=True)

    try:
        await run_crm_job(client, checkpoint_store)
        await run_multi_source_job(client, checkpoint_store)
    finally:
        await client.close()
# --8<-- [end:runner]
