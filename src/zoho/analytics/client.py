"""Zoho Analytics product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.analytics.bulk import AnalyticsBulkClient
    from zoho.analytics.data import AnalyticsDataClient
    from zoho.analytics.metadata import AnalyticsMetadataClient


class AnalyticsRequestCallable(Protocol):
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


class AnalyticsClient:
    """Product-scoped Analytics client."""

    def __init__(self, *, request: AnalyticsRequestCallable) -> None:
        self._request_fn = request
        self._metadata: AnalyticsMetadataClient | None = None
        self._data: AnalyticsDataClient | None = None
        self._bulk: AnalyticsBulkClient | None = None

    @property
    def metadata(self) -> AnalyticsMetadataClient:
        if self._metadata is None:
            from zoho.analytics.metadata import AnalyticsMetadataClient

            self._metadata = AnalyticsMetadataClient(self)
        return self._metadata

    @property
    def data(self) -> AnalyticsDataClient:
        if self._data is None:
            from zoho.analytics.data import AnalyticsDataClient

            self._data = AnalyticsDataClient(self)
        return self._data

    @property
    def bulk(self) -> AnalyticsBulkClient:
        if self._bulk is None:
            from zoho.analytics.bulk import AnalyticsBulkClient

            self._bulk = AnalyticsBulkClient(self)
        return self._bulk

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
