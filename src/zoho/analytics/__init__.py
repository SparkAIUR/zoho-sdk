"""Zoho Analytics namespace."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.analytics.client import AnalyticsClient

__all__ = ["AnalyticsClient"]


def __getattr__(name: str) -> Any:
    if name == "AnalyticsClient":
        from zoho.analytics.client import AnalyticsClient

        return AnalyticsClient
    raise AttributeError(f"module 'zoho.analytics' has no attribute {name!r}")
