"""Zoho CRM namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient
    from zoho.crm.models import Record

__all__ = ["CRMClient", "Record"]


def __getattr__(name: str) -> Any:
    if name == "CRMClient":
        from zoho.crm.client import CRMClient

        return CRMClient
    if name == "Record":
        from zoho.crm.models import Record

        return Record
    raise AttributeError(f"module 'zoho.crm' has no attribute {name!r}")
