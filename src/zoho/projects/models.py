"""Projects domain models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Portal(BaseModel):
    """Projects portal record."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str | None = None


class Project(BaseModel):
    """Projects project record."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str | None = None
    status: str | None = None


class Task(BaseModel):
    """Projects task record."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str | None = None
    status: str | None = None


class ProjectsResponse(BaseModel):
    """Common Projects response envelope."""

    model_config = ConfigDict(extra="allow")

    status: str | None = None
    message: str | None = None
    projects: list[Project] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    portals: list[Portal] = Field(default_factory=list)
    project: Project | None = None
    task: Task | None = None
    portal: Portal | None = None


def parse_projects_response(payload: Mapping[str, Any]) -> ProjectsResponse:
    """Convert raw Projects JSON payloads into typed envelope models."""

    return ProjectsResponse.model_validate(dict(payload))
