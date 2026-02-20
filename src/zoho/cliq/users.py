"""Cliq users APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.cliq.models import CliqResponse, parse_cliq_response

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient


class CliqUsersClient:
    """User management APIs for Zoho Cliq."""

    def __init__(self, cliq_client: CliqClient) -> None:
        self._cliq = cliq_client

    async def list(
        self,
        *,
        limit: int | None = None,
        modified_after: int | None = None,
        next_token: str | None = None,
        fields: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if modified_after is not None:
            params["modified_after"] = modified_after
        if next_token:
            params["next_token"] = next_token
        if fields:
            params["fields"] = fields

        payload = await self._cliq.request("GET", "/users", params=params, headers=headers)
        return parse_cliq_response(payload)

    async def get(self, *, user_id: str, headers: Mapping[str, str] | None = None) -> CliqResponse:
        payload = await self._cliq.request("GET", f"/users/{user_id}", headers=headers)
        return parse_cliq_response(payload)

    async def create(
        self,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", "/users", json=dict(data), headers=headers)
        return parse_cliq_response(payload)

    async def update(
        self,
        *,
        user_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "PUT", f"/users/{user_id}", json=dict(data), headers=headers
        )
        return parse_cliq_response(payload)
