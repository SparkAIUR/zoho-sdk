"""Zoho Creator namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.creator.client import CreatorClient

__all__ = ["CreatorClient"]


def __getattr__(name: str) -> Any:
    if name == "CreatorClient":
        from zoho.creator.client import CreatorClient

        return CreatorClient
    raise AttributeError(f"module 'zoho.creator' has no attribute {name!r}")
