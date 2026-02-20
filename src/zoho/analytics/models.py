"""Analytics domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict


class AnalyticsResponse(BaseModel):
    """Common Analytics response envelope."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    summary: str | None = None
    data: dict[str, Any] | list[dict[str, Any]] | None = None

    @property
    def result_rows(self) -> list[dict[str, Any]]:
        if isinstance(self.data, list):
            return [item for item in self.data if isinstance(item, dict)]
        if isinstance(self.data, dict):
            rows = self.data.get("data")
            if isinstance(rows, list):
                return [item for item in rows if isinstance(item, dict)]
            for key in (
                "orgs",
                "workspaces",
                "views",
                "dashboards",
                "users",
                "resources",
                "rows",
            ):
                value = self.data.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []


def parse_analytics_response(payload: Mapping[str, Any]) -> AnalyticsResponse:
    """Convert raw Analytics payloads into typed response models."""

    return AnalyticsResponse.model_validate(dict(payload))
