"""Zoho People namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.people.client import PeopleClient

__all__ = ["PeopleClient"]


def __getattr__(name: str) -> Any:
    if name == "PeopleClient":
        from zoho.people.client import PeopleClient

        return PeopleClient
    raise AttributeError(f"module 'zoho.people' has no attribute {name!r}")
