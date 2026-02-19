"""Creator metadata operations."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.creator.models import CreatorResponse, parse_creator_response

if TYPE_CHECKING:
    from zoho.creator.client import CreatorClient


class CreatorMetaClient:
    """High-usage Creator metadata operations.

    Example:
        ```python
        sections = await zoho.creator.meta.get_sections(
            account_owner_name="owner",
            app_link_name="app",
        )
        ```
    """

    def __init__(self, creator_client: CreatorClient) -> None:
        self._creator = creator_client

    async def get_sections(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "GET",
            f"/meta/{account_owner_name}/{app_link_name}/sections",
            headers=headers,
        )
        return parse_creator_response(payload)

    async def list_applications(
        self,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        payload = await self._creator.request(
            "GET",
            "/creator/v2/meta/applications",
            headers=headers,
        )
        applications = payload.get("applications")
        return (
            [item for item in applications if isinstance(item, dict)]
            if isinstance(applications, list)
            else []
        )

    async def list_applications_by_workspace(
        self,
        *,
        account_owner_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        payload = await self._creator.request(
            "GET",
            f"/creator/v2/meta/{account_owner_name}/applications",
            headers=headers,
        )
        applications = payload.get("applications")
        return (
            [item for item in applications if isinstance(item, dict)]
            if isinstance(applications, list)
            else []
        )

    async def get_forms(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "GET",
            f"/meta/{account_owner_name}/{app_link_name}/forms",
            headers=headers,
        )
        return parse_creator_response(payload)

    async def get_reports(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "GET",
            f"/meta/{account_owner_name}/{app_link_name}/reports",
            headers=headers,
        )
        return parse_creator_response(payload)

    async def get_form_fields(
        self,
        *,
        account_owner_name: str,
        app_link_name: str,
        form_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> CreatorResponse:
        payload = await self._creator.request(
            "GET",
            f"/meta/{account_owner_name}/{app_link_name}/form/{form_link_name}/fields",
            headers=headers,
        )
        return parse_creator_response(payload)
