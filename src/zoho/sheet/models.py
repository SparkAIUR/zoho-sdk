"""Sheet domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SheetResponse(BaseModel):
    """Common Sheet response envelope."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    message: str | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    workbooks: list[dict[str, Any]] = Field(default_factory=list)
    worksheets: list[dict[str, Any]] = Field(default_factory=list)
    records: list[dict[str, Any]] = Field(default_factory=list)


def parse_sheet_response(payload: Mapping[str, Any]) -> SheetResponse:
    """Convert raw Sheet payloads into typed response models."""

    return SheetResponse.model_validate(dict(payload))
