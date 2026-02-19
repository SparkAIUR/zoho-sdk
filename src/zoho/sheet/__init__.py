"""Zoho Sheet namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.sheet.client import SheetClient

__all__ = ["SheetClient"]


def __getattr__(name: str) -> Any:
    if name == "SheetClient":
        from zoho.sheet.client import SheetClient

        return SheetClient
    raise AttributeError(f"module 'zoho.sheet' has no attribute {name!r}")
