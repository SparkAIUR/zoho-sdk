"""Pipeshub AI ingestion adapter mapping for Zoho ingestion batches."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx
from pydantic import BaseModel, Field

from zoho.ingestion.models import IngestionDocument


# --8<-- [start:pipeshub_contract]
class PipeshubRecord(BaseModel):
    id: str
    source: str
    content: str | None = None
    title: str | None = None
    url: str | None = None
    updated_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
# --8<-- [end:pipeshub_contract]


# --8<-- [start:pipeshub_mapper]
def to_pipeshub_record(document: IngestionDocument) -> PipeshubRecord:
    return PipeshubRecord(
        id=document.id,
        source=document.source,
        content=document.content,
        title=document.title,
        url=document.url,
        updated_at=document.updated_at,
        metadata={
            **document.metadata,
            "mime_type": document.mime_type,
            "raw": document.raw,
        },
    )
# --8<-- [end:pipeshub_mapper]


# --8<-- [start:pipeshub_push]
async def upsert_pipeshub_batch(
    documents: Sequence[IngestionDocument],
    *,
    endpoint: str,
    api_key: str,
    dataset: str,
) -> None:
    payload = {
        "dataset": dataset,
        "records": [to_pipeshub_record(document).model_dump(mode="python") for document in documents],
    }

    async with httpx.AsyncClient(timeout=30.0) as http:
        response = await http.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        response.raise_for_status()
# --8<-- [end:pipeshub_push]
