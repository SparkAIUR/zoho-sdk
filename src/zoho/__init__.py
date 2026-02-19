"""Zoho SDK public package.

This package is intentionally lazy-loaded for fast startup.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zoho.client import Zoho
    from zoho.connections import ZohoConnectionProfile
    from zoho.settings import ZohoSettings

__all__ = ["Zoho", "ZohoConnectionProfile", "ZohoSettings", "__version__"]

try:
    __version__ = version("zoho")
except PackageNotFoundError:  # pragma: no cover - local editable installs before metadata exists
    __version__ = "0.1.1"


def __getattr__(name: str) -> Any:
    if name == "Zoho":
        from zoho.client import Zoho

        return Zoho
    if name == "ZohoSettings":
        from zoho.settings import ZohoSettings

        return ZohoSettings
    if name == "ZohoConnectionProfile":
        from zoho.connections import ZohoConnectionProfile

        return ZohoConnectionProfile
    raise AttributeError(f"module 'zoho' has no attribute {name!r}")
