"""Top-level Zoho SDK client."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from zoho.connections import ZohoConnectionProfile, ZohoConnectionsManager
from zoho.core.auth import OAuth2RefreshAuthProvider
from zoho.core.cache import AsyncTTLCache
from zoho.core.discovery_cache import DiscoveryDiskCache
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
    _default_discovery_cache_dir,
    _default_token_store_path,
)

if TYPE_CHECKING:
    from zoho.analytics.client import AnalyticsClient
    from zoho.cliq.client import CliqClient
    from zoho.creator.client import CreatorClient
    from zoho.crm.client import CRMClient
    from zoho.mail.client import MailClient
    from zoho.people.client import PeopleClient
    from zoho.projects.client import ProjectsClient
    from zoho.sheet.client import SheetClient
    from zoho.workdrive.client import WorkDriveClient
    from zoho.writer.client import WriterClient

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

_PEOPLE_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://people.zoho.com",
    "EU": "https://people.zoho.eu",
    "IN": "https://people.zoho.in",
    "AU": "https://people.zoho.com.au",
    "JP": "https://people.zoho.jp",
    "CA": "https://people.zohocloud.ca",
    "SA": "https://people.zoho.sa",
    "CN": "https://people.zoho.com.cn",
}

_SHEET_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://sheet.zoho.com",
    "EU": "https://sheet.zoho.eu",
    "IN": "https://sheet.zoho.in",
    "AU": "https://sheet.zoho.com.au",
    "JP": "https://sheet.zoho.jp",
    "CA": "https://sheet.zohocloud.ca",
    "SA": "https://sheet.zoho.sa",
    "CN": "https://sheet.zoho.com.cn",
}

_WORKDRIVE_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://www.zohoapis.com",
    "EU": "https://www.zohoapis.eu",
    "IN": "https://www.zohoapis.in",
    "AU": "https://www.zohoapis.com.au",
    "JP": "https://www.zohoapis.jp",
    "CA": "https://www.zohoapis.ca",
    "SA": "https://www.zohoapis.sa",
    "CN": "https://www.zohoapis.com.cn",
}

_CLIQ_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://cliq.zoho.com",
    "EU": "https://cliq.zoho.eu",
    "IN": "https://cliq.zoho.in",
    "AU": "https://cliq.zoho.com.au",
    "JP": "https://cliq.zoho.jp",
    "CA": "https://cliq.zohocloud.ca",
    "SA": "https://cliq.zoho.sa",
    "CN": "https://cliq.zoho.com.cn",
}

_ANALYTICS_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://analyticsapi.zoho.com",
    "EU": "https://analyticsapi.zoho.eu",
    "IN": "https://analyticsapi.zoho.in",
    "AU": "https://analyticsapi.zoho.com.au",
    "JP": "https://analyticsapi.zoho.jp",
    "CA": "https://analyticsapi.zohocloud.ca",
    "SA": "https://analyticsapi.zoho.sa",
    "CN": "https://analyticsapi.zoho.com.cn",
}

_WRITER_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://www.zohoapis.com",
    "EU": "https://www.zohoapis.eu",
    "IN": "https://www.zohoapis.in",
    "AU": "https://www.zohoapis.com.au",
    "JP": "https://www.zohoapis.jp",
    "CA": "https://www.zohoapis.ca",
    "SA": "https://www.zohoapis.sa",
    "CN": "https://www.zohoapis.com.cn",
}

_MAIL_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://mail.zoho.com",
    "EU": "https://mail.zoho.eu",
    "IN": "https://mail.zoho.in",
    "AU": "https://mail.zoho.com.au",
    "JP": "https://mail.zoho.jp",
    "CA": "https://mail.zohocloud.ca",
    "SA": "https://mail.zoho.sa",
    "CN": "https://mail.zoho.com.cn",
}

_DEFAULT_TOKEN_STORE_PATH = _default_token_store_path()
_DEFAULT_DISCOVERY_CACHE_DIR = _default_discovery_cache_dir()


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
            cache_namespace=settings.connection_name,
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
        self._discovery_cache: DiscoveryDiskCache | None = None
        if settings.cache.enable_discovery_cache:
            self._discovery_cache = DiscoveryDiskCache(
                base_dir=settings.cache.discovery_cache_dir,
                ttl_seconds=settings.cache.discovery_cache_ttl_seconds,
            )
        self._discovery_cache_scope = (
            f"{settings.connection_name}:{settings.dc}:{settings.environment}"
        )

        self._crm: CRMClient | None = None
        self._creator: CreatorClient | None = None
        self._projects: ProjectsClient | None = None
        self._people: PeopleClient | None = None
        self._sheet: SheetClient | None = None
        self._workdrive: WorkDriveClient | None = None
        self._cliq: CliqClient | None = None
        self._analytics: AnalyticsClient | None = None
        self._writer: WriterClient | None = None
        self._mail: MailClient | None = None

        self._connections: ZohoConnectionsManager | None = None
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
        connection_name: str = "default",
        accounts_domain: str | None = None,
        api_domain: str | None = None,
        creator_base_url: str | None = None,
        creator_environment_header: CreatorEnvironmentHeader | None = None,
        projects_base_url: str | None = None,
        projects_default_portal_id: str | None = None,
        people_base_url: str | None = None,
        sheet_base_url: str | None = None,
        workdrive_base_url: str | None = None,
        cliq_base_url: str | None = None,
        analytics_base_url: str | None = None,
        writer_base_url: str | None = None,
        mail_base_url: str | None = None,
        token_store_backend: TokenStoreBackend = "sqlite",
        token_store_path: Path = _DEFAULT_TOKEN_STORE_PATH,
        redis_url: str | None = None,
        log_format: LogFormat = "pretty",
        log_level: str = "INFO",
        user_agent: str = "zoho-sdk/0.1.3",
        timeout_seconds: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        verify_ssl: bool = True,
        max_retries: int = 3,
        backoff_base_seconds: float = 0.25,
        backoff_max_seconds: float = 5.0,
        enable_metadata_cache: bool = True,
        metadata_cache_ttl_seconds: int = 24 * 60 * 60,
        enable_discovery_cache: bool = True,
        discovery_cache_ttl_seconds: int = 24 * 60 * 60,
        discovery_cache_dir: Path = _DEFAULT_DISCOVERY_CACHE_DIR,
    ) -> Zoho:
        """Create a client with explicit configuration.

        This constructor is the recommended onboarding path for production usage.
        """

        settings = ZohoSettings(
            connection_name=connection_name,
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
            people_base_url=people_base_url,
            sheet_base_url=sheet_base_url,
            workdrive_base_url=workdrive_base_url,
            cliq_base_url=cliq_base_url,
            analytics_base_url=analytics_base_url,
            writer_base_url=writer_base_url,
            mail_base_url=mail_base_url,
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
                enable_discovery_cache=enable_discovery_cache,
                discovery_cache_ttl_seconds=discovery_cache_ttl_seconds,
                discovery_cache_dir=discovery_cache_dir.expanduser(),
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
                discovery_cache=self._discovery_cache,
                discovery_cache_scope=self._discovery_cache_scope,
            )
        return self._crm

    @property
    def creator(self) -> CreatorClient:
        """Access Zoho Creator operations."""

        if self._creator is None:
            from zoho.creator.client import CreatorClient

            self._creator = CreatorClient(
                request=self._request_creator,
                discovery_cache=self._discovery_cache,
                discovery_cache_scope=self._discovery_cache_scope,
            )
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
    def people(self) -> PeopleClient:
        """Access Zoho People operations."""

        if self._people is None:
            from zoho.people.client import PeopleClient

            self._people = PeopleClient(request=self._request_people)
        return self._people

    @property
    def sheet(self) -> SheetClient:
        """Access Zoho Sheet operations."""

        if self._sheet is None:
            from zoho.sheet.client import SheetClient

            self._sheet = SheetClient(request=self._request_sheet)
        return self._sheet

    @property
    def workdrive(self) -> WorkDriveClient:
        """Access Zoho WorkDrive operations."""

        if self._workdrive is None:
            from zoho.workdrive.client import WorkDriveClient

            self._workdrive = WorkDriveClient(request=self._request_workdrive)
        return self._workdrive

    @property
    def cliq(self) -> CliqClient:
        """Access Zoho Cliq operations."""

        if self._cliq is None:
            from zoho.cliq.client import CliqClient

            self._cliq = CliqClient(request=self._request_cliq)
        return self._cliq

    @property
    def analytics(self) -> AnalyticsClient:
        """Access Zoho Analytics operations."""

        if self._analytics is None:
            from zoho.analytics.client import AnalyticsClient

            self._analytics = AnalyticsClient(request=self._request_analytics)
        return self._analytics

    @property
    def writer(self) -> WriterClient:
        """Access Zoho Writer operations."""

        if self._writer is None:
            from zoho.writer.client import WriterClient

            self._writer = WriterClient(request=self._request_writer)
        return self._writer

    @property
    def mail(self) -> MailClient:
        """Access Zoho Mail operations."""

        if self._mail is None:
            from zoho.mail.client import MailClient

            self._mail = MailClient(request=self._request_mail)
        return self._mail

    @property
    def connections(self) -> ZohoConnectionsManager:
        """Access named connection profiles for multi-account usage."""

        if self._connections is None:
            self._connections = ZohoConnectionsManager(self)
        return self._connections

    def for_connection(self, name: str) -> Zoho:
        """Get a client view bound to a named connection profile."""

        if name == "default":
            return self
        return self.connections.get(name)

    def register_connection(self, profile: ZohoConnectionProfile) -> None:
        """Register an additional connection profile on this client."""

        self.connections.register(profile)

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

    async def _request_people(
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
            self.settings.people_base_url or _PEOPLE_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/people/") or clean_path.startswith("/api/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/people/api{clean_path}"

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

    async def _request_sheet(
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
            self.settings.sheet_base_url or _SHEET_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/api/v2/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/api/v2{clean_path}"

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

    async def _request_workdrive(
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
            self.settings.workdrive_base_url or _WORKDRIVE_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/workdrive/"):
            url = f"{base_domain}{clean_path}"
        elif clean_path.startswith("/api/v1/"):
            url = f"{base_domain}/workdrive{clean_path}"
        else:
            url = f"{base_domain}/workdrive/api/v1{clean_path}"

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

    async def _request_cliq(
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
            self.settings.cliq_base_url or _CLIQ_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/api/v2/") or clean_path.startswith("/network/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/api/v2{clean_path}"

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

    async def _request_analytics(
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
            self.settings.analytics_base_url or _ANALYTICS_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/restapi/v2/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/restapi/v2{clean_path}"

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

    async def _request_writer(
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
            self.settings.writer_base_url or _WRITER_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/writer/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/writer/api/v1{clean_path}"

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

    async def _request_mail(
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
            self.settings.mail_base_url or _MAIL_API_DOMAIN_BY_DC[self.settings.dc]
        ).rstrip("/")
        if clean_path.startswith("/api/"):
            url = f"{base_domain}{clean_path}"
        else:
            url = f"{base_domain}/api{clean_path}"

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

        if self._connections is not None:
            await self._connections.close_all()

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
