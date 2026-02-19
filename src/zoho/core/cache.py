"""Small async TTL cache used for metadata and schema lookups."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class _Entry(Generic[T]):
    value: T
    expires_at: float


class AsyncTTLCache(Generic[T]):
    """Simple in-memory TTL cache with async lock safety."""

    def __init__(self) -> None:
        self._entries: dict[str, _Entry[T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> T | None:
        async with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at < time.time():
                self._entries.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: T, ttl_seconds: int) -> None:
        expires_at = time.time() + max(ttl_seconds, 0)
        async with self._lock:
            self._entries[key] = _Entry(value=value, expires_at=expires_at)

    async def invalidate(self, key: str) -> None:
        async with self._lock:
            self._entries.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._entries.clear()
