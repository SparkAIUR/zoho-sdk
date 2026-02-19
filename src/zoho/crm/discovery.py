"""Runtime CRM submodule discovery and dynamic module clients."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from zoho.core.discovery_cache import DiscoveryDiskCache
from zoho.crm.models import ActionResponse, Record, RecordListResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from zoho.crm.client import CRMClient


_INVALID_CLASS_CHAR_PATTERN = re.compile(r"[^0-9A-Za-z_]+")


class CRMDynamicModuleClient:
    """Runtime-bound CRM module client.

    This wrapper keeps the high-usage record methods, but bakes in a module API name.
    """

    def __init__(
        self,
        crm_client: CRMClient,
        *,
        module_api_name: str,
        module_metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._crm = crm_client
        self._module_api_name = module_api_name
        self._module_metadata = dict(module_metadata or {})

    @property
    def module_api_name(self) -> str:
        return self._module_api_name

    @property
    def module_metadata(self) -> dict[str, Any]:
        return dict(self._module_metadata)

    async def get(
        self,
        *,
        record_id: str | int,
        fields: Sequence[str] | None = None,
    ) -> Record:
        return await self._crm.records.get(
            module=self._module_api_name,
            record_id=record_id,
            fields=fields,
        )

    async def list(
        self,
        *,
        page: int = 1,
        per_page: int = 200,
        fields: Sequence[str] | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> RecordListResponse:
        return await self._crm.records.list(
            module=self._module_api_name,
            page=page,
            per_page=per_page,
            fields=fields,
            extra_params=extra_params,
        )

    async def iter(
        self,
        *,
        per_page: int = 200,
        fields: Sequence[str] | None = None,
        extra_params: Mapping[str, Any] | None = None,
    ) -> AsyncIterator[Record]:
        async for record in self._crm.records.iter(
            module=self._module_api_name,
            per_page=per_page,
            fields=fields,
            extra_params=extra_params,
        ):
            yield record

    async def create(
        self,
        *,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        trigger: Sequence[str] | None = None,
    ) -> ActionResponse:
        return await self._crm.records.create(
            module=self._module_api_name,
            data=data,
            trigger=trigger,
        )

    async def update(
        self,
        *,
        record_id: str | int,
        data: Mapping[str, Any],
        trigger: Sequence[str] | None = None,
    ) -> ActionResponse:
        return await self._crm.records.update(
            module=self._module_api_name,
            record_id=record_id,
            data=data,
            trigger=trigger,
        )

    async def delete(self, *, record_id: str | int) -> ActionResponse:
        return await self._crm.records.delete(module=self._module_api_name, record_id=record_id)


def _dynamic_module_class_name(module_name: str) -> str:
    clean = _INVALID_CLASS_CHAR_PATTERN.sub("_", module_name).strip("_")
    if not clean:
        clean = "Module"
    if clean[0].isdigit():
        clean = f"_{clean}"
    return f"CRM{clean}ModuleClient"


class CRMDynamicNamespace:
    """Dynamic CRM namespace with runtime module discovery."""

    def __init__(
        self,
        crm_client: CRMClient,
        *,
        discovery_cache: DiscoveryDiskCache | None = None,
        discovery_cache_scope: str = "default:US:production",
    ) -> None:
        self._crm = crm_client
        self._clients: dict[str, CRMDynamicModuleClient] = {}
        self._dynamic_classes: dict[str, type[CRMDynamicModuleClient]] = {}
        self._module_metadata_by_name: dict[str, dict[str, Any]] = {}
        self._module_name_aliases: dict[str, str] = {}
        self._module_names: list[str] = []
        self._discovery_cache = discovery_cache
        self._discovery_cache_scope = discovery_cache_scope

    async def list_modules(
        self,
        *,
        use_cache: bool = True,
        cache_ttl_seconds: int | None = None,
    ) -> list[str]:
        if use_cache and self._module_names:
            return list(self._module_names)

        if use_cache and self._discovery_cache is not None:
            cached_modules = self._discovery_cache.load(
                product="crm",
                resource="modules",
                scope=self._discovery_cache_scope,
            )
            if cached_modules:
                self._ingest_module_metadata(cached_modules)
                return list(self._module_names)

        modules = await self._crm.modules.list(
            use_cache=use_cache,
            cache_ttl_seconds=cache_ttl_seconds,
        )
        self._ingest_module_metadata(modules)

        if self._discovery_cache is not None and modules:
            self._discovery_cache.save(
                product="crm",
                resource="modules",
                scope=self._discovery_cache_scope,
                entries=modules,
            )

        return list(self._module_names)

    async def has_module(
        self,
        name: str,
        *,
        use_cache: bool = True,
        cache_ttl_seconds: int | None = None,
    ) -> bool:
        await self.list_modules(use_cache=use_cache, cache_ttl_seconds=cache_ttl_seconds)
        return name.lower() in self._module_name_aliases

    async def get_module_client(
        self,
        name: str,
        *,
        use_cache: bool = True,
        cache_ttl_seconds: int | None = None,
    ) -> CRMDynamicModuleClient:
        await self.list_modules(use_cache=use_cache, cache_ttl_seconds=cache_ttl_seconds)
        canonical_name = self._module_name_aliases.get(name.lower())
        if canonical_name is None:
            sample = ", ".join(sorted(self._module_metadata_by_name)[:8])
            message = f"Unknown CRM module: {name!r}"
            if sample:
                message = f"{message}. Known modules include: {sample}"
            raise KeyError(message)
        return self._client_for_module(canonical_name)

    async def precompile_modules(
        self,
        *,
        cache_ttl_seconds: int | None = None,
    ) -> list[str]:
        """Force-refresh CRM module metadata and write it to disk cache."""

        return await self.list_modules(use_cache=False, cache_ttl_seconds=cache_ttl_seconds)

    def _client_for_module(self, module_name: str) -> CRMDynamicModuleClient:
        existing = self._clients.get(module_name)
        if existing is not None:
            return existing

        dynamic_class = self._dynamic_classes.get(module_name)
        if dynamic_class is None:
            class_name = _dynamic_module_class_name(module_name)
            dynamic_class = cast(
                type[CRMDynamicModuleClient],
                type(
                    class_name,
                    (CRMDynamicModuleClient,),
                    {
                        "__doc__": (
                            f"Runtime CRM module client for {module_name!r}. "
                            "Methods mirror `client.crm.records`."
                        )
                    },
                ),
            )
            self._dynamic_classes[module_name] = dynamic_class

        client = dynamic_class(
            self._crm,
            module_api_name=module_name,
            module_metadata=self._module_metadata_by_name.get(module_name),
        )
        self._clients[module_name] = client
        return client

    def __getattr__(self, name: str) -> CRMDynamicModuleClient:
        if name.startswith("_"):
            raise AttributeError(f"{self.__class__.__name__} has no attribute {name!r}")
        canonical_name = self._module_name_aliases.get(name.lower(), name)
        return self._client_for_module(canonical_name)

    def _ingest_module_metadata(self, modules: Sequence[Mapping[str, Any]]) -> None:
        names: list[str] = []
        metadata_map: dict[str, dict[str, Any]] = {}
        aliases: dict[str, str] = {}

        for module in modules:
            name_raw = module.get("api_name")
            if not isinstance(name_raw, str) or not name_raw:
                continue
            names.append(name_raw)
            metadata_map[name_raw] = dict(module)
            aliases[name_raw.lower()] = name_raw

        self._module_names = names
        self._module_metadata_by_name = metadata_map
        self._module_name_aliases = aliases
