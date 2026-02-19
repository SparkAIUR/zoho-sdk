"""Zoho CRM product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

from zoho.core.cache import AsyncTTLCache

if TYPE_CHECKING:
    from zoho.crm.discovery import CRMDynamicNamespace
    from zoho.crm.modules import ModulesClient
    from zoho.crm.org import OrgClient
    from zoho.crm.records import RecordsClient
    from zoho.crm.users import UsersClient


class CRMRequestCallable(Protocol):
    async def __call__(
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
    ) -> dict[str, Any]: ...


class CRMClient:
    """Product-scoped CRM client."""

    def __init__(
        self,
        *,
        request: CRMRequestCallable,
        metadata_cache: AsyncTTLCache[dict[str, Any]] | None,
        default_metadata_ttl_seconds: int,
    ) -> None:
        self._request_fn = request
        self._metadata_cache = metadata_cache
        self._default_metadata_ttl_seconds = default_metadata_ttl_seconds

        self._records: RecordsClient | None = None
        self._modules: ModulesClient | None = None
        self._org: OrgClient | None = None
        self._users: UsersClient | None = None
        self._dynamic: CRMDynamicNamespace | None = None

    @property
    def records(self) -> RecordsClient:
        if self._records is None:
            from zoho.crm.records import RecordsClient

            self._records = RecordsClient(self)
        return self._records

    @property
    def modules(self) -> ModulesClient:
        if self._modules is None:
            from zoho.crm.modules import ModulesClient

            self._modules = ModulesClient(self)
        return self._modules

    @property
    def org(self) -> OrgClient:
        if self._org is None:
            from zoho.crm.org import OrgClient

            self._org = OrgClient(self)
        return self._org

    @property
    def users(self) -> UsersClient:
        if self._users is None:
            from zoho.crm.users import UsersClient

            self._users = UsersClient(self)
        return self._users

    @property
    def dynamic(self) -> CRMDynamicNamespace:
        """Access runtime module discovery and dynamic module clients."""

        if self._dynamic is None:
            from zoho.crm.discovery import CRMDynamicNamespace

            self._dynamic = CRMDynamicNamespace(self)
        return self._dynamic

    async def request(
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
        use_cache: bool = False,
        cache_key: str | None = None,
        cache_ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        if use_cache and method.upper() == "GET" and self._metadata_cache is not None:
            key = cache_key or self._build_cache_key(method=method, path=path, params=params)
            cached = await self._metadata_cache.get(key)
            if cached is not None:
                return cached

            payload = await self._request_fn(
                method,
                path,
                headers=headers,
                params=params,
                json=json,
                data=data,
                files=files,
                timeout=timeout,
            )
            ttl = (
                cache_ttl_seconds
                if cache_ttl_seconds is not None
                else self._default_metadata_ttl_seconds
            )
            await self._metadata_cache.set(key, payload, ttl)
            return payload

        return await self._request_fn(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )

    @staticmethod
    def _build_cache_key(*, method: str, path: str, params: Mapping[str, Any] | None = None) -> str:
        parts = [method.upper(), path]
        if params:
            parts.extend(f"{key}={params[key]}" for key in sorted(params))
        return "|".join(parts)
