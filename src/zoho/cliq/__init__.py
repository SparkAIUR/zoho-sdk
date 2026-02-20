"""Zoho Cliq namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient

__all__ = ["CliqClient"]


def __getattr__(name: str) -> Any:
    if name == "CliqClient":
        from zoho.cliq.client import CliqClient

        return CliqClient
    raise AttributeError(f"module 'zoho.cliq' has no attribute {name!r}")
