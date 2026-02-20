"""Cliq domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict


class CliqResponse(BaseModel):
    """Common Cliq response envelope."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    message: str | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    next_token: str | None = None

    @property
    def result_rows(self) -> list[dict[str, Any]]:
        """Return the most likely list payload for collection APIs."""

        if isinstance(self.data, list):
            return [item for item in self.data if isinstance(item, dict)]
        if isinstance(self.data, dict):
            for key in (
                "data",
                "users",
                "channels",
                "chats",
                "messages",
                "threads",
                "members",
            ):
                value = self.data.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []


def parse_cliq_response(payload: Mapping[str, Any]) -> CliqResponse:
    """Convert raw Cliq payloads into typed response models."""

    return CliqResponse.model_validate(dict(payload))
