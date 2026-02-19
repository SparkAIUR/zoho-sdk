"""People domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict


class PeopleResponse(BaseModel):
    """Common People response envelope."""

    model_config = ConfigDict(extra="allow")

    code: int | str | None = None
    message: str | None = None
    response: dict[str, Any] | list[dict[str, Any]] | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None

    @property
    def result_rows(self) -> list[dict[str, Any]]:
        """Normalized list rows from `response.result`/`data` payloads."""

        if isinstance(self.response, dict):
            result = self.response.get("result")
            if isinstance(result, list):
                return [item for item in result if isinstance(item, dict)]
        if isinstance(self.response, list):
            return [item for item in self.response if isinstance(item, dict)]
        if isinstance(self.data, list):
            return [item for item in self.data if isinstance(item, dict)]
        if isinstance(self.data, dict):
            rows = self.data.get("result")
            if isinstance(rows, list):
                return [item for item in rows if isinstance(item, dict)]
        return []


def parse_people_response(payload: Mapping[str, Any]) -> PeopleResponse:
    """Convert raw People payloads into typed response models."""

    return PeopleResponse.model_validate(dict(payload))
