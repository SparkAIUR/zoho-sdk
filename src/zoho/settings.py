"""Typed SDK settings.

The SDK prefers explicit credential inputs, but this settings model also supports
`ZOHO_*` environment variables for convenience.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DataCenter = Literal["US", "EU", "IN", "AU", "JP", "CA", "SA", "CN"]
EnvironmentName = Literal["production", "sandbox", "developer"]
TokenStoreBackend = Literal["memory", "sqlite", "redis"]
LogFormat = Literal["pretty", "json"]
CreatorEnvironmentHeader = Literal["production", "development", "stage"]


def _default_token_store_path() -> Path:
    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if local_app_data:
            return Path(local_app_data) / "zoho" / "cache.sqlite3"
        return Path.home() / "AppData" / "Local" / "zoho" / "cache.sqlite3"
    return Path("~/.cache/zoho/cache.sqlite3").expanduser()


def _default_discovery_cache_dir() -> Path:
    if os.name == "nt":
        local_app_data = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if local_app_data:
            return Path(local_app_data) / "zohosdk"
        return Path.home() / "AppData" / "Local" / "zohosdk"
    return Path("~/.cache/zohosdk").expanduser()


class TransportSettings(BaseModel):
    """HTTP transport tuning knobs."""

    timeout_seconds: float = Field(default=30.0, gt=0)
    max_connections: int = Field(default=100, ge=1)
    max_keepalive_connections: int = Field(default=20, ge=1)
    verify_ssl: bool = True


class RetrySettings(BaseModel):
    """Retry behavior for transient failures."""

    max_retries: int = Field(default=3, ge=0, le=10)
    backoff_base_seconds: float = Field(default=0.25, gt=0)
    backoff_max_seconds: float = Field(default=5.0, gt=0)
    retry_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504)


class CacheSettings(BaseModel):
    """Cache behavior for metadata-heavy operations."""

    enable_metadata_cache: bool = True
    metadata_cache_ttl_seconds: int = Field(default=24 * 60 * 60, ge=0)
    enable_discovery_cache: bool = True
    discovery_cache_ttl_seconds: int = Field(default=24 * 60 * 60, ge=0)
    discovery_cache_dir: Path = Field(default_factory=_default_discovery_cache_dir)


class ZohoSettings(BaseSettings):
    """Top-level SDK configuration.

    Environment variable support is available via `ZOHO_*` keys.
    Example: `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`.
    """

    model_config = SettingsConfigDict(
        env_prefix="ZOHO_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    client_id: str = Field(min_length=1)
    client_secret: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    dc: DataCenter = "US"
    environment: EnvironmentName = "production"
    connection_name: str = "default"

    accounts_domain: str | None = None
    api_domain: str | None = None
    creator_base_url: str | None = None
    creator_environment_header: CreatorEnvironmentHeader | None = None
    projects_base_url: str | None = None
    projects_default_portal_id: str | None = None
    people_base_url: str | None = None
    sheet_base_url: str | None = None
    workdrive_base_url: str | None = None
    cliq_base_url: str | None = None
    analytics_base_url: str | None = None
    writer_base_url: str | None = None
    mail_base_url: str | None = None

    user_agent: str = "zoho-sdk/0.1.3"

    token_store_backend: TokenStoreBackend = "sqlite"
    token_store_path: Path = Field(default_factory=_default_token_store_path)
    redis_url: str | None = None

    log_format: LogFormat = "pretty"
    log_level: str = "INFO"

    transport: TransportSettings = Field(default_factory=TransportSettings)
    retry: RetrySettings = Field(default_factory=RetrySettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
