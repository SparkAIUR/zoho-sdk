"""Zoho Mail namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.mail.client import MailClient

__all__ = ["MailClient"]


def __getattr__(name: str) -> Any:
    if name == "MailClient":
        from zoho.mail.client import MailClient

        return MailClient
    raise AttributeError(f"module 'zoho.mail' has no attribute {name!r}")
