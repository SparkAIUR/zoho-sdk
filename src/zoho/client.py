"""Top-level Zoho SDK client."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from zoho.core.auth import OAuth2RefreshAuthProvider
from zoho.core.cache import AsyncTTLCache
from zoho.core.logging import configure_logging, get_logger
from zoho.core.token_store import TokenStore, build_token_store
from zoho.core.transport import HttpxTransport
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
)

if TYPE_CHECKING:
    from zoho.creator.client import CreatorClient
    from zoho.crm.client import CRMClient
    from zoho.projects.client import ProjectsClient

_PROJECTS_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://projectsapi.zoho.com",
    "EU": "https://projectsapi.zoho.eu",
    "IN": "https://projectsapi.zoho.in",
    "AU": "https://projectsapi.zoho.com.au",
    "JP": "https://projectsapi.zoho.jp",
    "CA": "https://projectsapi.zohocloud.ca",
    "SA": "https://projectsapi.zoho.sa",
    "CN": "https://projectsapi.zoho.com.cn",
}


class Zoho:
    """Async first SDK entry point.

    Example:
        ```python
        from zoho import Zoho

        # one-shot scripts / jobs
        async with Zoho.from_credentials(
            client_id="...",
            client_secret="...",
            refresh_token="...",
        ) as zoho:
            lead = await zoho.crm.records.get(module="Leads", record_id="123456789")
            print(lead.id)

        # long-lived app singleton
        zoho = Zoho.from_credentials(
            client_id="...",
            client_secret="...",
            refresh_token="...",
        )
        lead = await zoho.crm.records.get(module="Leads", record_id="123456789")
        await zoho.close()
        ```
    """

    def __init__(self, settings: ZohoSettings, *, token_store: TokenStore | None = None) -> None:
        self.settings = settings

        configure_logging(log_format=settings.log_format, log_level=settings.log_level)
        self._logger = get_logger("zoho.client")

        self._token_store = token_store or build_token_store(
            backend=settings.token_store_backend,
            sqlite_path=settings.token_store_path,
            redis_url=settings.redis_url,
        )

        self._auth = OAuth2RefreshAuthProvider(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            refresh_token=settings.refresh_token,
            dc=settings.dc,
            environment=settings.environment,
            token_store=self._token_store,
            accounts_domain=settings.accounts_domain,
            api_domain=settings.api_domain,
            user_agent=settings.user_agent,
        )

        self._transport = HttpxTransport(
            timeout_seconds=settings.transport.timeout_seconds,
            max_connections=settings.transport.max_connections,
            max_keepalive_connections=settings.transport.max_keepalive_connections,
            verify_ssl=settings.transport.verify_ssl,
            max_retries=settings.retry.max_retries,
            backoff_base_seconds=settings.retry.backoff_base_seconds,
            backoff_max_seconds=settings.retry.backoff_max_seconds,
            retry_status_codes=settings.retry.retry_status_codes,
        )

        self._metadata_cache: AsyncTTLCache[dict[str, Any]] | None = None
        if settings.cache.enable_metadata_cache:
            self._metadata_cache = AsyncTTLCache()

        self._crm: CRMClient | None = None
        self._creator: CreatorClient | None = None
        self._projects: ProjectsClient | None = None
        self._closed = False

    @classmethod
    def from_settings(cls, settings: ZohoSettings) -> Zoho:
        return cls(settings)

    @classmethod
    def from_env(cls) -> Zoho:
        """Create a client from `ZOHO_*` environment variables."""

        return cls(ZohoSettings())  # type: ignore[call-arg]

    @classmethod
    def from_credentials(
        cls,
        *,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        dc: DataCenter = "US",
        environment: EnvironmentName = "production",
        accounts_domain: str | None = None,
        api_domain: str | None = None,
        creator_base_url: str | None = None,
        creator_environment_header: CreatorEnvironmentHeader | None = None,
        projects_base_url: str | None = None,
        projects_default_portal_id: str | None = None,
        token_store_backend: TokenStoreBackend = "sqlite",
        token_store_path: Path = Path("~/.cache/zoho/cache.sqlite3"),
        redis_url: str | None = None,
        log_format: LogFormat = "pretty",
        log_level: str = "INFO",
        user_agent: str = "zoho-sdk/0.1.0",
        timeout_seconds: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        verify_ssl: bool = True,
        max_retries: int = 3,
        backoff_base_seconds: float = 0.25,
        backoff_max_seconds: float = 5.0,
        enable_metadata_cache: bool = True,
        metadata_cache_ttl_seconds: int = 24 * 60 * 60,
    ) -> Zoho:
        """Create a client with explicit configuration.

        This constructor is the recommended onboarding path for production usage.
        """

        settings = ZohoSettings(
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            dc=dc,
            environment=environment,
            accounts_domain=accounts_domain,
            api_domain=api_domain,
            creator_base_url=creator_base_url,
            creator_environment_header=creator_environment_header,
            projects_base_url=projects_base_url,
            projects_default_portal_id=projects_default_portal_id,
            token_store_backend=token_store_backend,
            token_store_path=token_store_path.expanduser(),
            redis_url=redis_url,
            log_format=log_format,
            log_level=log_level,
            user_agent=user_agent,
            transport=TransportSettings(
                timeout_seconds=timeout_seconds,
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                verify_ssl=verify_ssl,
            ),
            retry=RetrySettings(
                max_retries=max_retries,
                backoff_base_seconds=backoff_base_seconds,
                backoff_max_seconds=backoff_max_seconds,
            ),
            cache=CacheSettings(
                enable_metadata_cache=enable_metadata_cache,
                metadata_cache_ttl_seconds=metadata_cache_ttl_seconds,
            ),
        )
        return cls(settings)

    @property
    def crm(self) -> CRMClient:
        """Access Zoho CRM operations."""

        if self._crm is None:
            from zoho.crm.client import CRMClient

            self._crm = CRMClient(
                request=self._request_crm,
                metadata_cache=self._metadata_cache,
                default_metadata_ttl_seconds=self.settings.cache.metadata_cache_ttl_seconds,
            )
        return self._crm

    @property
    def creator(self) -> CreatorClient:
        """Access Zoho Creator operations."""

        if self._creator is None:
            from zoho.creator.client import CreatorClient

            self._creator = CreatorClient(request=self._request_creator)
        return self._creator

    @property
    def projects(self) -> ProjectsClient:
        """Access Zoho Projects operations."""

        if self._projects is None:
            from zoho.projects.client import ProjectsClient

            self._projects = ProjectsClient(
                request=self._request_projects,
                default_portal_id=self.settings.projects_default_portal_id,
            )
        return self._projects

    @property
    def closed(self) -> bool:
        """Whether the client lifecycle has been closed."""

        return self._closed

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError(
                "Zoho client is closed. Create a new client instance or keep a long-lived "
                "singleton open until app shutdown."
            )

    async def _request_crm(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self._ensure_open()
        clean_path = path if path.startswith("/") else f"/{path}"

        api_domain = await self._auth.get_api_domain()
        url = f"{api_domain}/crm/v8{clean_path}"

        auth_headers = await self._auth.get_auth_headers()
        request_headers = {
            "Accept": "application/json",
            "User-Agent": self.settings.user_agent,
            **auth_headers,
            **dict(headers or {}),
        }

        response = await self._transport.request(
            method,
            url,
            headers=request_headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
        return self._parse_response(response)

    async def _request_creator(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self._ensure_open()
        clean_path = path if path.startswith("/") else f"/{path}"

        base_domain = (self.settings.creator_base_url or await self._auth.get_api_domain()).rstrip(
            "/"
        )
        if clean_path.startswith("/creator/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/creator/v2.1{clean_path}"

        auth_headers = await self._auth.get_auth_headers()
        request_headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": self.settings.user_agent,
            **auth_headers,
        }
        if self.settings.creator_environment_header is not None:
            request_headers["environment"] = self.settings.creator_environment_header
        request_headers.update(dict(headers or {}))

        response = await self._transport.request(
            method,
            url,
            headers=request_headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
        return self._parse_response(response)

    async def _request_projects(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        self._ensure_open()
        clean_path = path if path.startswith("/") else f"/{path}"

        base_domain = (
            self.settings.projects_base_url or _PROJECTS_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/api/v3/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/api/v3{clean_path}"

        auth_headers = await self._auth.get_auth_headers()
        request_headers = {
            "Accept": "application/json",
            "User-Agent": self.settings.user_agent,
            **auth_headers,
            **dict(headers or {}),
        }

        response = await self._transport.request(
            method,
            url,
            headers=request_headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response: Any) -> dict[str, Any]:
        if response.status_code == 204 or not response.content:
            return {}

        try:
            payload = response.json()
        except ValueError:
            return {"raw": response.text}

        if isinstance(payload, Mapping):
            return dict(payload)
        return {"data": cast(list[Any], payload)}

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        await self._auth.close()
        await self._transport.close()
        self._logger.info("zoho_client_closed")

    async def aclose(self) -> None:
        await self.close()

    async def __aenter__(self) -> Zoho:
        self._ensure_open()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()
