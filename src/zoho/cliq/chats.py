"""Cliq chats APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.cliq.models import CliqResponse, parse_cliq_response

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient


class CliqChatsClient:
    """Direct chat APIs for Zoho Cliq."""

    def __init__(self, cliq_client: CliqClient) -> None:
        self._cliq = cliq_client

    async def list(
        self,
        *,
        limit: int | None = None,
        next_token: str | None = None,
        modified_before: int | None = None,
        modified_after: int | None = None,
        drafts: bool | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if next_token:
            params["next_token"] = next_token
        if modified_before is not None:
            params["modified_before"] = modified_before
        if modified_after is not None:
            params["modified_after"] = modified_after
        if drafts is not None:
            params["drafts"] = drafts

        payload = await self._cliq.request("GET", "/chats", params=params, headers=headers)
        return parse_cliq_response(payload)

    async def list_members(
        self,
        *,
        chat_id: str,
        fields: str | None = None,
        limit: int | None = None,
        next_token: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        if limit is not None:
            params["limit"] = limit
        if next_token:
            params["next_token"] = next_token

        payload = await self._cliq.request(
            "GET",
            f"/chats/{chat_id}/members",
            params=params,
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def mute(self, *, chat_id: str, headers: Mapping[str, str] | None = None) -> CliqResponse:
        payload = await self._cliq.request("POST", f"/chats/{chat_id}/mute", headers=headers)
        return parse_cliq_response(payload)

    async def unmute(
        self, *, chat_id: str, headers: Mapping[str, str] | None = None
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", f"/chats/{chat_id}/unmute", headers=headers)
        return parse_cliq_response(payload)

    async def leave(
        self, *, chat_id: str, headers: Mapping[str, str] | None = None
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", f"/chats/{chat_id}/leave", headers=headers)
        return parse_cliq_response(payload)
