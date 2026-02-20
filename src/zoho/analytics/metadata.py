"""Analytics metadata APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from zoho.analytics.models import AnalyticsResponse, parse_analytics_response

if TYPE_CHECKING:
    from zoho.analytics.client import AnalyticsClient


class AnalyticsMetadataClient:
    """Metadata APIs for Zoho Analytics."""

    def __init__(self, analytics_client: AnalyticsClient) -> None:
        self._analytics = analytics_client

    async def list_organizations(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request("GET", "/orgs", headers=headers)
        return parse_analytics_response(payload)

    async def list_workspaces(
        self,
        *,
        owned: bool = False,
        shared: bool = False,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        path = "/workspaces"
        if owned:
            path = "/workspaces/owned"
        elif shared:
            path = "/workspaces/shared"

        payload = await self._analytics.request("GET", path, headers=headers)
        return parse_analytics_response(payload)

    async def get_workspace(
        self,
        *,
        workspace_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/workspaces/{workspace_id}",
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def list_views(
        self,
        *,
        workspace_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request(
            "GET",
            f"/workspaces/{workspace_id}/views",
            headers=headers,
        )
        return parse_analytics_response(payload)

    async def get_view(
        self,
        *,
        view_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request("GET", f"/views/{view_id}", headers=headers)
        return parse_analytics_response(payload)

    async def list_dashboards(
        self,
        *,
        owned: bool = False,
        shared: bool = False,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        path = "/dashboards"
        if owned:
            path = "/dashboards/owned"
        elif shared:
            path = "/dashboards/shared"

        payload = await self._analytics.request("GET", path, headers=headers)
        return parse_analytics_response(payload)

    async def get_metadata_details(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> AnalyticsResponse:
        payload = await self._analytics.request("GET", "/metadetails", headers=headers)
        return parse_analytics_response(payload)
