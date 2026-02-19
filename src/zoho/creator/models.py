"""Creator domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CreatorRecord(BaseModel):
    """Dynamic Creator record container with permissive fields."""

    model_config = ConfigDict(extra="allow")


class CreatorResponse(BaseModel):
    """Common Creator response envelope."""

    model_config = ConfigDict(extra="allow")

    code: int | str | None = None
    message: str | None = None
    data: list[CreatorRecord] = Field(default_factory=list)
    result: dict[str, Any] | list[dict[str, Any]] | None = None

    @property
    def first_data(self) -> CreatorRecord | None:
        if self.data:
            return self.data[0]
        return None


def parse_creator_response(payload: Mapping[str, Any]) -> CreatorResponse:
    """Convert raw Creator JSON payloads into typed envelope models."""

    return CreatorResponse.model_validate(dict(payload))
