from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from zoho.core.token_store import MemoryTokenStore, OAuthToken, SQLiteTokenStore


async def test_memory_token_store_roundtrip() -> None:
    store = MemoryTokenStore()
    token = OAuthToken(
        access_token="token",
        refresh_token="refresh",
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )

    await store.save("k", token)
    loaded = await store.load("k")

    assert loaded is not None
    assert loaded.access_token == "token"
    assert loaded.refresh_token == "refresh"


async def test_memory_refresh_lock_serializes_access() -> None:
    store = MemoryTokenStore()
    order: list[str] = []

    async def worker(name: str) -> None:
        async with store.refresh_lock("shared"):
            order.append(name)
            await asyncio.sleep(0.02)

    await asyncio.gather(worker("a"), worker("b"))

    assert sorted(order) == ["a", "b"]
    assert order in (["a", "b"], ["b", "a"])


async def test_sqlite_token_store_roundtrip(tmp_path) -> None:
    store = SQLiteTokenStore(tmp_path / "tokens.sqlite3")
    token = OAuthToken(
        access_token="sqlite-token",
        refresh_token="sqlite-refresh",
        expires_at=datetime.now(UTC) + timedelta(minutes=30),
    )

    await store.save("k", token)
    loaded = await store.load("k")

    assert loaded is not None
    assert loaded.access_token == "sqlite-token"
    assert loaded.refresh_token == "sqlite-refresh"
