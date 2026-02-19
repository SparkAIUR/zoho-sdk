"""WorkDrive domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkDriveResource(BaseModel):
    """JSON:API-like WorkDrive resource."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    type: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    relationships: dict[str, Any] = Field(default_factory=dict)
    links: dict[str, Any] = Field(default_factory=dict)


class WorkDriveResponse(BaseModel):
    """Common WorkDrive response envelope."""

    model_config = ConfigDict(extra="allow")

    data: WorkDriveResource | list[WorkDriveResource] | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    links: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, Any]] = Field(default_factory=list)

    @property
    def resources(self) -> list[WorkDriveResource]:
        if isinstance(self.data, list):
            return self.data
        if isinstance(self.data, WorkDriveResource):
            return [self.data]
        return []


def parse_workdrive_response(payload: Mapping[str, Any]) -> WorkDriveResponse:
    """Convert raw WorkDrive payloads into typed response models."""

    return WorkDriveResponse.model_validate(dict(payload))
