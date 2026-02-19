"""Zoho WorkDrive namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.workdrive.client import WorkDriveClient

__all__ = ["WorkDriveClient"]


def __getattr__(name: str) -> Any:
    if name == "WorkDriveClient":
        from zoho.workdrive.client import WorkDriveClient

        return WorkDriveClient
    raise AttributeError(f"module 'zoho.workdrive' has no attribute {name!r}")
