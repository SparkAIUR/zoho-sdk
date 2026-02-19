"""Zoho Projects namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.projects.client import ProjectsClient

__all__ = ["ProjectsClient"]


def __getattr__(name: str) -> Any:
    if name == "ProjectsClient":
        from zoho.projects.client import ProjectsClient

        return ProjectsClient
    raise AttributeError(f"module 'zoho.projects' has no attribute {name!r}")
