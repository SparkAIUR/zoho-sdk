"""Cliq messages APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.cliq.models import CliqResponse, parse_cliq_response

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient


class CliqMessagesClient:
    """Message APIs for Zoho Cliq."""

    def __init__(self, cliq_client: CliqClient) -> None:
        self._cliq = cliq_client

    async def list(
        self,
        *,
        chat_id: str,
        from_time: int | None = None,
        to_time: int | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if from_time is not None:
            params["fromtime"] = from_time
        if to_time is not None:
            params["totime"] = to_time
        if limit is not None:
            params["limit"] = limit

        payload = await self._cliq.request(
            "GET",
            f"/chats/{chat_id}/messages",
            params=params,
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def get(
        self,
        *,
        chat_id: str,
        message_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "GET",
            f"/chats/{chat_id}/messages/{message_id}",
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def post_to_channel(
        self,
        *,
        channel_unique_name: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "POST",
            f"/channelsbyname/{channel_unique_name}/message",
            json=dict(data),
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def post_to_chat(
        self,
        *,
        chat_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "POST",
            f"/chats/{chat_id}/message",
            json=dict(data),
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def update(
        self,
        *,
        chat_id: str,
        message_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "PUT",
            f"/chats/{chat_id}/messages/{message_id}",
            json=dict(data),
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def delete(
        self,
        *,
        chat_id: str,
        message_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "DELETE",
            f"/chats/{chat_id}/messages/{message_id}",
            headers=headers,
        )
        return parse_cliq_response(payload)
