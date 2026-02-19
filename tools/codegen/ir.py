"""Intermediate representation (IR) models for code generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True, frozen=True)
class ModelDef:
    id: str
    field_count: int
    interface: bool


@dataclass(slots=True, frozen=True)
class EndpointDef:
    id: str
    method: str
    path: str
    operation_id: str
    group: str


@dataclass(slots=True)
class IRSummary:
    model_count: int
    interface_count: int
    field_count: int
    endpoint_count: int
    spec_type_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
