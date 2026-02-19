"""Multi-account connection profiles and manager."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from zoho.settings import (
    CacheSettings,
    CreatorEnvironmentHeader,
    DataCenter,
    EnvironmentName,
    LogFormat,
    RetrySettings,
    TokenStoreBackend,
    TransportSettings,
    ZohoSettings,
    _default_discovery_cache_dir,
    _default_token_store_path,
)

if TYPE_CHECKING:
    from zoho.client import Zoho


class ZohoConnectionProfile(BaseModel):
    """Explicit account profile for registering additional Zoho connections."""

    name: str = Field(min_length=1)

    client_id: str = Field(min_length=1)
    client_secret: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    dc: DataCenter = "US"
    environment: EnvironmentName = "production"

    accounts_domain: str | None = None
    api_domain: str | None = None

    creator_base_url: str | None = None
    creator_environment_header: CreatorEnvironmentHeader | None = None

    projects_base_url: str | None = None
    projects_default_portal_id: str | None = None

    people_base_url: str | None = None
    sheet_base_url: str | None = None
    workdrive_base_url: str | None = None

    token_store_backend: TokenStoreBackend = "sqlite"
    token_store_path: Path = Field(default_factory=_default_token_store_path)
    redis_url: str | None = None

    log_format: LogFormat = "pretty"
    log_level: str = "INFO"
    user_agent: str = "zoho-sdk/0.1.1"

    timeout_seconds: float = 30.0
    max_connections: int = 100
    max_keepalive_connections: int = 20
    verify_ssl: bool = True

    max_retries: int = 3
    backoff_base_seconds: float = 0.25
    backoff_max_seconds: float = 5.0

    enable_metadata_cache: bool = True
    metadata_cache_ttl_seconds: int = 24 * 60 * 60
    enable_discovery_cache: bool = True
    discovery_cache_ttl_seconds: int = 24 * 60 * 60
    discovery_cache_dir: Path = Field(default_factory=_default_discovery_cache_dir)

    def to_settings(self) -> ZohoSettings:
        """Build typed runtime settings for this connection profile."""

        return ZohoSettings(
            connection_name=self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
            dc=self.dc,
            environment=self.environment,
            accounts_domain=self.accounts_domain,
            api_domain=self.api_domain,
            creator_base_url=self.creator_base_url,
            creator_environment_header=self.creator_environment_header,
            projects_base_url=self.projects_base_url,
            projects_default_portal_id=self.projects_default_portal_id,
            people_base_url=self.people_base_url,
            sheet_base_url=self.sheet_base_url,
            workdrive_base_url=self.workdrive_base_url,
            token_store_backend=self.token_store_backend,
            token_store_path=self.token_store_path.expanduser(),
            redis_url=self.redis_url,
            log_format=self.log_format,
            log_level=self.log_level,
            user_agent=self.user_agent,
            transport=TransportSettings(
                timeout_seconds=self.timeout_seconds,
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
                verify_ssl=self.verify_ssl,
            ),
            retry=RetrySettings(
                max_retries=self.max_retries,
                backoff_base_seconds=self.backoff_base_seconds,
                backoff_max_seconds=self.backoff_max_seconds,
            ),
            cache=CacheSettings(
                enable_metadata_cache=self.enable_metadata_cache,
                metadata_cache_ttl_seconds=self.metadata_cache_ttl_seconds,
                enable_discovery_cache=self.enable_discovery_cache,
                discovery_cache_ttl_seconds=self.discovery_cache_ttl_seconds,
                discovery_cache_dir=self.discovery_cache_dir.expanduser(),
            ),
        )


class ZohoConnectionsManager:
    """Manage named account profiles for multi-tenant connector workloads."""

    def __init__(self, default_client: Zoho) -> None:
        self._default_client = default_client
        self._profiles: dict[str, ZohoConnectionProfile] = {}
        self._clients: dict[str, Zoho] = {"default": default_client}

    def register(self, profile: ZohoConnectionProfile) -> None:
        if profile.name == "default":
            msg = "'default' is reserved for the root client connection"
            raise ValueError(msg)
        if profile.name in self._clients:
            raise ValueError(f"connection {profile.name!r} already exists")

        from zoho.client import Zoho

        connection_client = Zoho.from_settings(profile.to_settings())
        self._profiles[profile.name] = profile
        self._clients[profile.name] = connection_client

    def get(self, name: str) -> Zoho:
        try:
            return self._clients[name]
        except KeyError as exc:
            raise KeyError(f"Unknown connection {name!r}") from exc

    def list(self) -> list[str]:
        return sorted(self._clients)

    async def remove(self, name: str, *, close: bool = True) -> None:
        if name == "default":
            raise ValueError("Cannot remove the default connection")
        client = self._clients.pop(name, None)
        self._profiles.pop(name, None)
        if client is not None and close:
            await client.close()

    async def close_all(self) -> None:
        names = [name for name in self._clients if name != "default"]
        for name in names:
            client = self._clients.pop(name)
            await client.close()
            self._profiles.pop(name, None)
