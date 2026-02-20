"""Analytics bulk/import-export APIs."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.analytics.models import AnalyticsResponse, parse_analytics_response

if TYPE_CHECKING:
    from zoho.analytics.client import AnalyticsClient


def _config_params(config: Mapping[str, Any] | None) -> dict[str, Any]:
    if not config:
        return {}
    return {"CONFIG": json.dumps(dict(config), separators=(",", ":"), ensure_ascii=True)}


class AnalyticsBulkClient:
    """Bulk and asynchronous job APIs for Zoho Analytics."""

    def __init__(self, analytics_client: AnalyticsClient) -> None:
        self._analytics = analytics_client

    async def import_data(
        self,
        *,
        workspace_id: str,
        config: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "POST",
            f"/bulk/workspaces/{workspace_id}/data",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def export_data(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/bulk/workspaces/{workspace_id}/views/{view_id}/data",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def get_import_job(
        self,
        *,
        workspace_id: str,
        job_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/bulk/workspaces/{workspace_id}/importjobs/{job_id}",
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def get_export_job(
        self,
        *,
        workspace_id: str,
        job_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/bulk/workspaces/{workspace_id}/exportjobs/{job_id}",
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def download_export_job(
        self,
        *,
        workspace_id: str,
        job_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/bulk/workspaces/{workspace_id}/exportjobs/{job_id}/data",
            headers=headers,
        )
        return parse_analytics_response(payload)
