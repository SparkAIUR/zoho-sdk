"""Runtime Creator application discovery and dynamic app clients."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, cast

from zoho.core.discovery_cache import DiscoveryDiskCache
from zoho.creator.models import CreatorResponse

if TYPE_CHECKING:
    from zoho.creator.client import CreatorClient


_INVALID_CLASS_CHAR_PATTERN = re.compile(r"[^0-9A-Za-z_]+")


class CreatorDynamicMetaClient:
    """Meta API wrapper bound to one Creator application."""

    def __init__(self, app_client: CreatorDynamicApplicationClient) -> None:
        self._app = app_client

    async def get_sections(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.meta.get_sections(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            headers=headers,
        )

    async def get_forms(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.meta.get_forms(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            headers=headers,
        )

    async def get_reports(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.meta.get_reports(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            headers=headers,
        )

    async def get_form_fields(
        self,
        *,
        form_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.meta.get_form_fields(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            form_link_name=form_link_name,
            headers=headers,
        )


class CreatorDynamicDataClient:
    """Data API wrapper bound to one Creator application."""

    def __init__(self, app_client: CreatorDynamicApplicationClient) -> None:
        self._app = app_client

    async def list_records(
        self,
        *,
        report_link_name: str,
        from_index: int | None = None,
        limit: int | None = None,
        criteria: str | None = None,
        record_cursor: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.data.list_records(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            from_index=from_index,
            limit=limit,
            criteria=criteria,
            record_cursor=record_cursor,
            headers=headers,
        )

    async def add_records(
        self,
        *,
        form_link_name: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        skip_workflow: Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.data.add_records(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            form_link_name=form_link_name,
            data=data,
            skip_workflow=skip_workflow,
            headers=headers,
        )

    async def update_record(
        self,
        *,
        report_link_name: str,
        record_id: str | int,
        data: Mapping[str, Any],
        skip_workflow: Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.data.update_record(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            record_id=record_id,
            data=data,
            skip_workflow=skip_workflow,
            headers=headers,
        )

    async def delete_record(
        self,
        *,
        report_link_name: str,
        record_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.data.delete_record(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            record_id=record_id,
            headers=headers,
        )


class CreatorDynamicPublishClient:
    """Publish API wrapper bound to one Creator application."""

    def __init__(self, app_client: CreatorDynamicApplicationClient) -> None:
        self._app = app_client

    async def list_records(
        self,
        *,
        report_link_name: str,
        from_index: int | None = None,
        limit: int | None = None,
        criteria: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.publish.list_records(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            from_index=from_index,
            limit=limit,
            criteria=criteria,
            headers=headers,
        )

    async def add_records(
        self,
        *,
        form_link_name: str,
        data: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.publish.add_records(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            form_link_name=form_link_name,
            data=data,
            headers=headers,
        )

    async def update_record(
        self,
        *,
        report_link_name: str,
        record_id: str | int,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.publish.update_record(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            record_id=record_id,
            data=data,
            headers=headers,
        )

    async def delete_record(
        self,
        *,
        report_link_name: str,
        record_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        return await self._app._creator.publish.delete_record(
            account_owner_name=self._app.account_owner_name,
            app_link_name=self._app.app_link_name,
            report_link_name=report_link_name,
            record_id=record_id,
            headers=headers,
        )


class CreatorDynamicApplicationClient:
    """Runtime-bound Creator application client."""

    def __init__(
        self,
        creator_client: CreatorClient,
        *,
        account_owner_name: str,
        app_link_name: str,
        application_metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self._creator = creator_client
        self._account_owner_name = account_owner_name
        self._app_link_name = app_link_name
        self._application_metadata = dict(application_metadata or {})
        self._meta: CreatorDynamicMetaClient | None = None
        self._data: CreatorDynamicDataClient | None = None
        self._publish: CreatorDynamicPublishClient | None = None

    @property
    def account_owner_name(self) -> str:
        return self._account_owner_name

    @property
    def app_link_name(self) -> str:
        return self._app_link_name

    @property
    def application_metadata(self) -> dict[str, Any]:
        return dict(self._application_metadata)

    @property
    def meta(self) -> CreatorDynamicMetaClient:
        if self._meta is None:
            self._meta = CreatorDynamicMetaClient(self)
        return self._meta

    @property
    def data(self) -> CreatorDynamicDataClient:
        if self._data is None:
            self._data = CreatorDynamicDataClient(self)
        return self._data

    @property
    def publish(self) -> CreatorDynamicPublishClient:
        if self._publish is None:
            self._publish = CreatorDynamicPublishClient(self)
        return self._publish


def _dynamic_application_class_name(app_link_name: str) -> str:
    clean = _INVALID_CLASS_CHAR_PATTERN.sub("_", app_link_name).strip("_")
    parts = [part for part in clean.split("_") if part]
    pascal_name = "".join(part[:1].upper() + part[1:] for part in parts)
    if not pascal_name:
        pascal_name = "Application"
    if pascal_name[0].isdigit():
        pascal_name = f"_{pascal_name}"
    return f"Creator{pascal_name}ApplicationClient"


class CreatorDynamicNamespace:
    """Dynamic Creator namespace with runtime application discovery."""

    def __init__(
        self,
        creator_client: CreatorClient,
        *,
        discovery_cache: DiscoveryDiskCache | None = None,
        discovery_cache_scope: str = "default:US:production",
    ) -> None:
        self._creator = creator_client
        self._clients: dict[str, CreatorDynamicApplicationClient] = {}
        self._dynamic_classes: dict[str, type[CreatorDynamicApplicationClient]] = {}
        self._application_metadata_by_key: dict[str, dict[str, Any]] = {}
        self._application_aliases: dict[str, str] = {}
        self._application_list: list[dict[str, Any]] = []
        self._last_loaded_scope: str | None = None
        self._discovery_cache = discovery_cache
        self._discovery_cache_scope = discovery_cache_scope

    async def list_applications(
        self,
        *,
        account_owner_name: str | None = None,
        use_cache: bool = True,
    ) -> list[dict[str, Any]]:
        scope = self._scope_for_workspace(account_owner_name)

        if use_cache and self._last_loaded_scope == scope and self._application_list:
            return list(self._application_list)

        if use_cache and self._discovery_cache is not None:
            cached = self._discovery_cache.load(
                product="creator",
                resource="applications",
                scope=scope,
            )
            if cached:
                self._ingest_applications(cached, account_owner_hint=account_owner_name, scope=scope)
                return list(self._application_list)

        applications = (
            await self._creator.meta.list_applications_by_workspace(
                account_owner_name=account_owner_name,
            )
            if account_owner_name
            else await self._creator.meta.list_applications()
        )
        self._ingest_applications(applications, account_owner_hint=account_owner_name, scope=scope)

        if self._discovery_cache is not None and applications:
            self._discovery_cache.save(
                product="creator",
                resource="applications",
                scope=scope,
                entries=applications,
            )

        return list(self._application_list)

    async def has_application(
        self,
        name: str,
        *,
        account_owner_name: str | None = None,
        use_cache: bool = True,
    ) -> bool:
        await self.list_applications(account_owner_name=account_owner_name, use_cache=use_cache)
        return self._resolve_application_key(name) is not None

    async def get_application_client(
        self,
        name: str,
        *,
        account_owner_name: str | None = None,
        use_cache: bool = True,
    ) -> CreatorDynamicApplicationClient:
        await self.list_applications(account_owner_name=account_owner_name, use_cache=use_cache)
        canonical_key = self._resolve_application_key(name)
        if canonical_key is None:
            sample = ", ".join(sorted(self._application_aliases)[:8])
            message = f"Unknown Creator application: {name!r}"
            if sample:
                message = f"{message}. Known applications include: {sample}"
            raise KeyError(message)
        return self._client_for_application(canonical_key)

    async def precompile_applications(
        self,
        *,
        account_owner_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """Force-refresh Creator applications and write them to disk cache."""

        return await self.list_applications(account_owner_name=account_owner_name, use_cache=False)

    def __getattr__(self, name: str) -> CreatorDynamicApplicationClient:
        if name.startswith("_"):
            raise AttributeError(f"{self.__class__.__name__} has no attribute {name!r}")
        canonical_key = self._resolve_application_key(name)
        if canonical_key is None:
            raise AttributeError(
                f"{self.__class__.__name__} has no dynamic application {name!r}; "
                "call list_applications() first."
            )
        return self._client_for_application(canonical_key)

    def _scope_for_workspace(self, account_owner_name: str | None) -> str:
        if account_owner_name is None:
            return self._discovery_cache_scope
        return f"{self._discovery_cache_scope}|workspace={account_owner_name}"

    @staticmethod
    def _application_key(account_owner_name: str, app_link_name: str) -> str:
        return f"{account_owner_name.lower()}:{app_link_name.lower()}"

    @staticmethod
    def _extract_application_identity(
        app: Mapping[str, Any],
        *,
        account_owner_hint: str | None,
    ) -> tuple[str | None, str | None]:
        app_link_name_raw = (
            app.get("link_name")
            or app.get("app_link_name")
            or app.get("application_link_name")
        )
        account_owner_raw = (
            app.get("workspace_name")
            or app.get("account_owner_name")
            or app.get("created_by")
            or account_owner_hint
        )
        app_link_name = (
            app_link_name_raw.strip()
            if isinstance(app_link_name_raw, str) and app_link_name_raw.strip()
            else None
        )
        account_owner_name = (
            account_owner_raw.strip()
            if isinstance(account_owner_raw, str) and account_owner_raw.strip()
            else None
        )
        return account_owner_name, app_link_name

    def _ingest_applications(
        self,
        applications: Sequence[Mapping[str, Any]],
        *,
        account_owner_hint: str | None,
        scope: str,
    ) -> None:
        metadata_by_key: dict[str, dict[str, Any]] = {}
        aliases: dict[str, str] = {}
        list_payload: list[dict[str, Any]] = []
        app_keys_by_link_name: dict[str, list[str]] = {}
        app_keys_by_attr_alias: dict[str, list[str]] = {}

        for app in applications:
            account_owner_name, app_link_name = self._extract_application_identity(
                app,
                account_owner_hint=account_owner_hint,
            )
            if account_owner_name is None or app_link_name is None:
                continue

            app_key = self._application_key(account_owner_name, app_link_name)
            metadata = dict(app)
            metadata.setdefault("account_owner_name", account_owner_name)
            metadata.setdefault("app_link_name", app_link_name)
            metadata_by_key[app_key] = metadata
            list_payload.append(metadata)

            aliases[app_key] = app_key
            aliases[f"{account_owner_name.lower()}.{app_link_name.lower()}"] = app_key
            app_keys_by_link_name.setdefault(app_link_name.lower(), []).append(app_key)
            attr_alias = app_link_name.lower().replace("-", "_")
            app_keys_by_attr_alias.setdefault(attr_alias, []).append(app_key)

        for app_link_name, app_keys in app_keys_by_link_name.items():
            if len(app_keys) == 1:
                aliases[app_link_name] = app_keys[0]
        for attr_alias, app_keys in app_keys_by_attr_alias.items():
            if len(app_keys) == 1:
                aliases[attr_alias] = app_keys[0]

        self._application_metadata_by_key = metadata_by_key
        self._application_aliases = aliases
        self._application_list = list_payload
        self._last_loaded_scope = scope

    def _resolve_application_key(self, name: str) -> str | None:
        name_key = name.lower()
        resolved = self._application_aliases.get(name_key)
        if resolved is not None:
            return resolved
        return self._application_aliases.get(name_key.replace("-", "_"))

    def _client_for_application(self, app_key: str) -> CreatorDynamicApplicationClient:
        existing = self._clients.get(app_key)
        if existing is not None:
            return existing

        metadata = self._application_metadata_by_key.get(app_key)
        if metadata is None:
            raise KeyError(f"Unknown Creator application key: {app_key!r}")

        account_owner_name = cast(str, metadata["account_owner_name"])
        app_link_name = cast(str, metadata["app_link_name"])

        dynamic_class = self._dynamic_classes.get(app_key)
        if dynamic_class is None:
            class_name = _dynamic_application_class_name(app_link_name)
            dynamic_class = cast(
                type[CreatorDynamicApplicationClient],
                type(
                    class_name,
                    (CreatorDynamicApplicationClient,),
                    {
                        "__doc__": (
                            f"Runtime Creator application client for {account_owner_name!r}/"
                            f"{app_link_name!r}."
                        )
                    },
                ),
            )
            self._dynamic_classes[app_key] = dynamic_class

        client = dynamic_class(
            self._creator,
            account_owner_name=account_owner_name,
            app_link_name=app_link_name,
            application_metadata=metadata,
        )
        self._clients[app_key] = client
        return client
