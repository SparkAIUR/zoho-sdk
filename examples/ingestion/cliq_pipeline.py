"""Reusable Cliq ingestion workflow skeleton for connector jobs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from zoho import Zoho
from zoho.ingestion import (
    iter_cliq_channel_documents,
    iter_cliq_chat_documents,
    iter_cliq_thread_documents,
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


# --8<-- [start:channel_chat_job]
async def run_channel_chat_job(client: Zoho, checkpoint_store: JsonCheckpointStore) -> None:
    channel_checkpoint = checkpoint_store.load("cliq_channels")
    async for batch in iter_cliq_channel_documents(
        client,
        checkpoint=channel_checkpoint,
        page_size=200,
        max_pages=10,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("cliq_channels", batch.checkpoint)

    chat_checkpoint = checkpoint_store.load("cliq_chats")
    async for batch in iter_cliq_chat_documents(
        client,
        checkpoint=chat_checkpoint,
        include_messages=True,
        message_limit=200,
        page_size=200,
        max_pages=10,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("cliq_chats", batch.checkpoint)


# --8<-- [end:channel_chat_job]


# --8<-- [start:thread_job]
async def run_thread_job(
    client: Zoho,
    checkpoint_store: JsonCheckpointStore,
    *,
    chat_id: str,
) -> None:
    thread_checkpoint = checkpoint_store.load("cliq_threads")
    async for batch in iter_cliq_thread_documents(
        client,
        chat_id=chat_id,
        checkpoint=thread_checkpoint,
        max_threads=50,
    ):
        await index_documents(batch.documents)
        checkpoint_store.save("cliq_threads", batch.checkpoint)


# --8<-- [end:thread_job]


# --8<-- [start:runner]
async def run_cliq_connector() -> None:
    client = Zoho.from_credentials(
        client_id="${ZOHO_CLIENT_ID}",
        client_secret="${ZOHO_CLIENT_SECRET}",
        refresh_token="${ZOHO_REFRESH_TOKEN}",
    )

    checkpoint_store = JsonCheckpointStore(Path(".checkpoints/zoho-cliq.json"))
    checkpoint_store._path.parent.mkdir(parents=True, exist_ok=True)

    try:
        await run_channel_chat_job(client, checkpoint_store)
        await run_thread_job(client, checkpoint_store, chat_id="chat_123")
    finally:
        await client.close()


# --8<-- [end:runner]
