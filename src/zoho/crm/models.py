"""CRM domain models."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableMapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PageInfo(BaseModel):
    """Pagination details returned by list endpoints."""

    per_page: int | None = None
    count: int | None = None
    page: int | None = None
    more_records: bool = False
    next_page_token: str | None = None


class RecordListResponse(BaseModel):
    """Structured record list response."""

    data: list[dict[str, Any]] = Field(default_factory=list)
    info: PageInfo | None = None


class ActionResponse(BaseModel):
    """Action response envelope used by create/update/delete operations."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    code: str | None = None
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class Record(MutableMapping[str, Any]):
    """Ergonomic dynamic CRM record mapping.

    Example:
        ```python
        record = Record({"Last_Name": "Ng", "Email": "jane@example.com"})
        record["Company"] = "Acme"
        payload = record.to_dict()
        ```
    """

    def __init__(self, initial: Mapping[str, Any] | None = None) -> None:
        self._values: dict[str, Any] = dict(initial or {})

    @property
    def id(self) -> str | None:
        value = self._values.get("id")
        return str(value) if value is not None else None

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)

    def __getitem__(self, key: str) -> Any:
        return self._values[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._values[key] = value

    def __delitem__(self, key: str) -> None:
        del self._values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)


def extract_first_data(payload: Mapping[str, Any]) -> dict[str, Any]:
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        return {}
    first = data[0]
    return first if isinstance(first, dict) else {}
