"""Writer domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict


class WriterResponse(BaseModel):
    """Common Writer response envelope."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    message: str | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None

    @property
    def result_rows(self) -> list[dict[str, Any]]:
        if isinstance(self.data, list):
            return [item for item in self.data if isinstance(item, dict)]
        if isinstance(self.data, dict):
            for key in ("documents", "folders", "data", "records"):
                value = self.data.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []


def parse_writer_response(payload: Mapping[str, Any]) -> WriterResponse:
    """Convert raw Writer payloads into typed response models."""

    return WriterResponse.model_validate(dict(payload))
