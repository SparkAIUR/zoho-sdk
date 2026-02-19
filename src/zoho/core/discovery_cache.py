"""Persistent discovery cache for dynamic product metadata."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Mapping, Sequence
from contextlib import suppress
from pathlib import Path
from typing import Any

_SAFE_PATH_COMPONENT = re.compile(r"[^0-9A-Za-z._-]+")


def _safe_component(value: str) -> str:
    safe = _SAFE_PATH_COMPONENT.sub("_", value).strip("._")
    return safe or "default"


class DiscoveryDiskCache:
    """Small JSON-file cache for discovery metadata.

    Entries are namespaced by product/resource/scope and expired by TTL.
    """

    def __init__(self, *, base_dir: Path, ttl_seconds: int) -> None:
        self._base_dir = base_dir.expanduser()
        self._ttl_seconds = max(ttl_seconds, 0)

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds

    def load(
        self,
        *,
        product: str,
        resource: str,
        scope: str,
    ) -> list[dict[str, Any]] | None:
        cache_file = self._cache_file(product=product, resource=resource, scope=scope)
        if not cache_file.is_file():
            return None

        try:
            payload_raw = json.loads(cache_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(payload_raw, dict):
            return None

        expires_at = payload_raw.get("expires_at")
        if not isinstance(expires_at, (int, float)) or expires_at <= time.time():
            return None

        entries_raw = payload_raw.get("entries")
        if not isinstance(entries_raw, list):
            return None

        entries: list[dict[str, Any]] = []
        for item in entries_raw:
            if isinstance(item, Mapping):
                entries.append(dict(item))
        return entries

    def save(
        self,
        *,
        product: str,
        resource: str,
        scope: str,
        entries: Sequence[Mapping[str, Any]],
    ) -> None:
        if self._ttl_seconds <= 0:
            return

        cache_file = self._cache_file(product=product, resource=resource, scope=scope)
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "cached_at": time.time(),
            "expires_at": time.time() + self._ttl_seconds,
            "entries": [dict(item) for item in entries],
        }

        tmp_file = cache_file.with_suffix(".tmp")
        try:
            payload_text = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
            tmp_file.write_text(payload_text, encoding="utf-8")
            tmp_file.replace(cache_file)
        except OSError:
            with suppress(OSError):
                tmp_file.unlink(missing_ok=True)

    def invalidate(self, *, product: str, resource: str, scope: str) -> None:
        cache_file = self._cache_file(product=product, resource=resource, scope=scope)
        with suppress(OSError):
            cache_file.unlink(missing_ok=True)

    def _cache_file(self, *, product: str, resource: str, scope: str) -> Path:
        product_component = _safe_component(product)
        resource_component = _safe_component(resource)
        scope_component = _safe_component(scope)
        return self._base_dir / product_component / f"{resource_component}_{scope_component}.json"
