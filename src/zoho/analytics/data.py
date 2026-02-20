"""Analytics data APIs."""

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


class AnalyticsDataClient:
    """Data row APIs for Zoho Analytics."""

    def __init__(self, analytics_client: AnalyticsClient) -> None:
        self._analytics = analytics_client

    async def create_rows(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "POST",
            f"/workspaces/{workspace_id}/views/{view_id}/rows",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def list_rows(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/workspaces/{workspace_id}/views/{view_id}/rows",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def update_rows(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "PUT",
            f"/workspaces/{workspace_id}/views/{view_id}/rows",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def delete_rows(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "DELETE",
            f"/workspaces/{workspace_id}/views/{view_id}/rows",
            params=_config_params(config),
            headers=headers,
        )
        return parse_analytics_response(payload)
