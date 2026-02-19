"""Zoho Creator product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.creator.data import CreatorDataClient
    from zoho.creator.meta import CreatorMetaClient
    from zoho.creator.publish import CreatorPublishClient


class CreatorRequestCallable(Protocol):
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


class CreatorClient:
    """Product-scoped Creator client.

    Example:
        ```python
        forms = await zoho.creator.meta.get_forms(
            account_owner_name="owner",
            app_link_name="inventory_app",
        )
        print(forms.code)
        ```
    """

    def __init__(self, *, request: CreatorRequestCallable) -> None:
        self._request_fn = request
        self._meta: CreatorMetaClient | None = None
        self._data: CreatorDataClient | None = None
        self._publish: CreatorPublishClient | None = None

    @property
    def meta(self) -> CreatorMetaClient:
        if self._meta is None:
            from zoho.creator.meta import CreatorMetaClient

            self._meta = CreatorMetaClient(self)
        return self._meta

    @property
    def data(self) -> CreatorDataClient:
        if self._data is None:
            from zoho.creator.data import CreatorDataClient

            self._data = CreatorDataClient(self)
        return self._data

    @property
    def publish(self) -> CreatorPublishClient:
        if self._publish is None:
            from zoho.creator.publish import CreatorPublishClient

            self._publish = CreatorPublishClient(self)
        return self._publish

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
    ) -> dict[str, Any]:
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
