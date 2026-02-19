"""Oynx (enterprise search) adapter mapping for Zoho ingestion batches."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx
from pydantic import BaseModel, Field

from zoho.ingestion.models import IngestionDocument


# --8<-- [start:oynx_contract]
class OynxDocument(BaseModel):
    external_id: str
    source: str
    title: str | None = None
    text: str | None = None
    url: str | None = None
    updated_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
# --8<-- [end:oynx_contract]


# --8<-- [start:oynx_mapper]
def to_oynx_document(document: IngestionDocument) -> OynxDocument:
    return OynxDocument(
        external_id=document.id,
        source=document.source,
        title=document.title,
        text=document.content,
        url=document.url,
        updated_at=document.updated_at,
        metadata={
            **document.metadata,
            "mime_type": document.mime_type,
        },
    )
# --8<-- [end:oynx_mapper]


# --8<-- [start:oynx_push]
async def push_oynx_batch(
    documents: Sequence[IngestionDocument],
    *,
    endpoint: str,
    api_key: str,
    tenant_id: str,
) -> None:
    payload = {
        "tenant": tenant_id,
        "documents": [to_oynx_document(document).model_dump(mode="python") for document in documents],
    }

    async with httpx.AsyncClient(timeout=30.0) as http:
        response = await http.post(
            endpoint,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
        response.raise_for_status()
# --8<-- [end:oynx_push]
