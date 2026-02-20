"""Cliq channels APIs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.cliq.models import CliqResponse, parse_cliq_response

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient


class CliqChannelsClient:
    """Channel APIs for Zoho Cliq."""

    def __init__(self, cliq_client: CliqClient) -> None:
        self._cliq = cliq_client

    async def list(
        self,
        *,
        name: str | None = None,
        status: str | None = None,
        level: str | None = None,
        limit: int | None = None,
        next_token: str | None = None,
        modified_before: int | None = None,
        modified_after: int | None = None,
        created_before: int | None = None,
        created_after: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if name:
            params["name"] = name
        if status:
            params["status"] = status
        if level:
            params["level"] = level
        if limit is not None:
            params["limit"] = limit
        if next_token:
            params["next_token"] = next_token
        if modified_before is not None:
            params["modified_before"] = modified_before
        if modified_after is not None:
            params["modified_after"] = modified_after
        if created_before is not None:
            params["created_before"] = created_before
        if created_after is not None:
            params["created_after"] = created_after

        payload = await self._cliq.request("GET", "/channels", params=params, headers=headers)
        return parse_cliq_response(payload)

    async def get(
        self,
        *,
        channel_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("GET", f"/channels/{channel_id}", headers=headers)
        return parse_cliq_response(payload)

    async def create(
        self,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", "/channels", json=dict(data), headers=headers)
        return parse_cliq_response(payload)

    async def update(
        self,
        *,
        channel_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "PUT",
            f"/channels/{channel_id}",
            json=dict(data),
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def delete(
        self,
        *,
        channel_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("DELETE", f"/channels/{channel_id}", headers=headers)
        return parse_cliq_response(payload)

    async def list_members(
        self,
        *,
        channel_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "GET", f"/channels/{channel_id}/members", headers=headers
        )
        return parse_cliq_response(payload)

    async def add_members(
        self,
        *,
        channel_id: str,
        user_ids: Sequence[str],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "POST",
            f"/channels/{channel_id}/members",
            json={"user_ids": list(user_ids)},
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def remove_members(
        self,
        *,
        channel_id: str,
        user_ids: Sequence[str],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "DELETE",
            f"/channels/{channel_id}/members",
            json={"user_ids": list(user_ids)},
            headers=headers,
        )
        return parse_cliq_response(payload)
