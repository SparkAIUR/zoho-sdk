"""Token persistence backends for OAuth refresh tokens."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import sqlite3
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol, cast

from pydantic import BaseModel, Field

redis_asyncio: Any
try:
    import redis.asyncio as redis_asyncio
except ImportError:  # pragma: no cover - optional dependency
    redis_asyncio = None


class OAuthToken(BaseModel):
    """Persisted OAuth token representation."""

    access_token: str
    expires_at: datetime
    refresh_token: str | None = None
    api_domain: str | None = None
    scope: tuple[str, ...] = Field(default_factory=tuple)
    token_type: str = "Zoho-oauthtoken"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def is_expired(self, *, skew_seconds: int = 30) -> bool:
        return self.expires_at <= datetime.now(UTC) + timedelta(seconds=skew_seconds)


class TokenStore(Protocol):
    """Token store protocol used by auth providers."""

    async def load(self, key: str) -> OAuthToken | None: ...

    async def save(self, key: str, token: OAuthToken) -> None: ...

    def refresh_lock(
        self, key: str, *, ttl_seconds: int = 30, wait_timeout_seconds: float = 10.0
    ) -> contextlib.AbstractAsyncContextManager[None]: ...


class MemoryTokenStore:
    """In-memory token store for tests and ephemeral processes."""

    def __init__(self) -> None:
        self._tokens: dict[str, OAuthToken] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def load(self, key: str) -> OAuthToken | None:
        return self._tokens.get(key)

    async def save(self, key: str, token: OAuthToken) -> None:
        token.updated_at = datetime.now(UTC)
        self._tokens[key] = token

    def _get_lock(self, key: str) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    @asynccontextmanager
    async def refresh_lock(
        self, key: str, *, ttl_seconds: int = 30, wait_timeout_seconds: float = 10.0
    ) -> AsyncIterator[None]:
        _ = ttl_seconds
        _ = wait_timeout_seconds
        lock = self._get_lock(key)
        await lock.acquire()
        try:
            yield
        finally:
            lock.release()


class SQLiteTokenStore:
    """SQLite-backed token store with cross-process refresh locking."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()
        self._initialized = False
        self._init_lock = asyncio.Lock()

    async def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        async with self._init_lock:
            if self._initialized:
                return
            await asyncio.to_thread(self._initialize_db)
            self._initialized = True

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._path), timeout=30)

    def _initialize_db(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tokens (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS locks (
                    key TEXT PRIMARY KEY,
                    owner TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    async def load(self, key: str) -> OAuthToken | None:
        await self._ensure_initialized()
        return await asyncio.to_thread(self._load_sync, key)

    def _load_sync(self, key: str) -> OAuthToken | None:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM tokens WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        return OAuthToken.model_validate_json(row[0])

    async def save(self, key: str, token: OAuthToken) -> None:
        await self._ensure_initialized()
        token.updated_at = datetime.now(UTC)
        await asyncio.to_thread(self._save_sync, key, token)

    def _save_sync(self, key: str, token: OAuthToken) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tokens(key, value, expires_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    expires_at=excluded.expires_at,
                    updated_at=excluded.updated_at
                """,
                (
                    key,
                    token.model_dump_json(),
                    int(token.expires_at.timestamp()),
                    int(time.time()),
                ),
            )
            conn.commit()

    def _try_acquire_lock(self, key: str, owner: str, ttl_seconds: int) -> bool:
        now = int(time.time())
        expires_at = now + ttl_seconds
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM locks WHERE key = ? AND expires_at <= ?", (key, now))
            try:
                conn.execute(
                    "INSERT INTO locks(key, owner, expires_at) VALUES (?, ?, ?)",
                    (key, owner, expires_at),
                )
            except sqlite3.IntegrityError:
                conn.rollback()
                return False
            conn.commit()
            return True

    def _release_lock(self, key: str, owner: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM locks WHERE key = ? AND owner = ?", (key, owner))
            conn.commit()

    @asynccontextmanager
    async def refresh_lock(
        self, key: str, *, ttl_seconds: int = 30, wait_timeout_seconds: float = 10.0
    ) -> AsyncIterator[None]:
        await self._ensure_initialized()

        owner = uuid.uuid4().hex
        acquired = False
        deadline = time.monotonic() + wait_timeout_seconds

        while time.monotonic() < deadline:
            acquired = await asyncio.to_thread(self._try_acquire_lock, key, owner, ttl_seconds)
            if acquired:
                break
            await asyncio.sleep(0.1)

        if not acquired:
            raise TimeoutError(f"Unable to acquire token refresh lock for key={key!r}")

        try:
            yield
        finally:
            await asyncio.to_thread(self._release_lock, key, owner)


class RedisTokenStore:
    """Redis-backed token store for distributed worker deployments."""

    def __init__(self, redis_url: str) -> None:
        if redis_asyncio is None:  # pragma: no cover - optional dependency
            raise ImportError("redis extra is required for RedisTokenStore")
        self._client = redis_asyncio.from_url(redis_url, decode_responses=True)

    @staticmethod
    def _token_key(key: str) -> str:
        return f"zoho:token:{key}"

    @staticmethod
    def _lock_key(key: str) -> str:
        return f"zoho:lock:{key}"

    async def load(self, key: str) -> OAuthToken | None:
        raw = await self._client.get(self._token_key(key))
        if raw is None:
            return None
        return OAuthToken.model_validate_json(raw)

    async def save(self, key: str, token: OAuthToken) -> None:
        token.updated_at = datetime.now(UTC)
        ttl_seconds = max(int((token.expires_at - datetime.now(UTC)).total_seconds()), 1)
        await self._client.set(self._token_key(key), token.model_dump_json(), ex=ttl_seconds)

    @asynccontextmanager
    async def refresh_lock(
        self, key: str, *, ttl_seconds: int = 30, wait_timeout_seconds: float = 10.0
    ) -> AsyncIterator[None]:
        lock_key = self._lock_key(key)
        owner = uuid.uuid4().hex
        acquired = False

        deadline = time.monotonic() + wait_timeout_seconds
        while time.monotonic() < deadline:
            acquired = bool(await self._client.set(lock_key, owner, nx=True, ex=ttl_seconds))
            if acquired:
                break
            await asyncio.sleep(0.1)

        if not acquired:
            raise TimeoutError(f"Unable to acquire token refresh lock for key={key!r}")

        try:
            yield
        finally:
            # Compare-and-delete to avoid removing someone else's lock.
            script = (
                "if redis.call('GET', KEYS[1]) == ARGV[1] then "
                "return redis.call('DEL', KEYS[1]) else return 0 end"
            )
            eval_result = self._client.eval(script, 1, lock_key, owner)
            if inspect.isawaitable(eval_result):
                await cast(Any, eval_result)


def build_token_store(*, backend: str, sqlite_path: Path, redis_url: str | None) -> TokenStore:
    """Create a concrete token store backend from settings."""

    if backend == "memory":
        return MemoryTokenStore()
    if backend == "sqlite":
        return SQLiteTokenStore(sqlite_path)
    if backend == "redis":
        if not redis_url:
            raise ValueError("redis_url is required when token_store_backend='redis'")
        return RedisTokenStore(redis_url)
    raise ValueError(f"Unsupported token store backend: {backend}")
