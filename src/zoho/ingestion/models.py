"""Normalized ingestion models for connector workloads."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IngestionCheckpoint(BaseModel):
    """Serializable checkpoint for resumable crawls."""

    cursor: str | None = None
    offset: int | None = None
    page: int | None = None
    updated_at: str | None = None
    extras: dict[str, Any] = Field(default_factory=dict)


class IngestionDocument(BaseModel):
    """Normalized document shape for index pipelines."""

    id: str
    source: str
    title: str | None = None
    content: str | None = None
    mime_type: str | None = None
    url: str | None = None
    updated_at: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class IngestionBatch(BaseModel):
    """Batch payload yielded by ingestion iterators."""

    source: str
    documents: list[IngestionDocument] = Field(default_factory=list)
    checkpoint: IngestionCheckpoint | None = None
