"""Zoho Writer namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.writer.client import WriterClient

__all__ = ["WriterClient"]


def __getattr__(name: str) -> Any:
    if name == "WriterClient":
        from zoho.writer.client import WriterClient

        return WriterClient
    raise AttributeError(f"module 'zoho.writer' has no attribute {name!r}")
