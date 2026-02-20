"""Cliq threads APIs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.cliq.models import CliqResponse, parse_cliq_response

if TYPE_CHECKING:
    from zoho.cliq.client import CliqClient


class CliqThreadsClient:
    """Thread APIs for Zoho Cliq."""

    def __init__(self, cliq_client: CliqClient) -> None:
        self._cliq = cliq_client

    async def post_message(
        self,
        *,
        thread_id: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "POST",
            f"/threads/{thread_id}/message",
            json=dict(data),
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def list_followers(
        self,
        *,
        thread_id: str,
        limit: int | None = None,
        next_token: str | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if next_token:
            params["next_token"] = next_token

        payload = await self._cliq.request(
            "GET",
            f"/threads/{thread_id}/followers",
            params=params,
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def add_followers(
        self,
        *,
        thread_id: str,
        user_ids: Sequence[str],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "POST",
            f"/threads/{thread_id}/followers",
            json={"user_ids": list(user_ids)},
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def remove_followers(
        self,
        *,
        thread_id: str,
        user_ids: Sequence[str],
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "DELETE",
            f"/threads/{thread_id}/followers",
            json={"user_ids": list(user_ids)},
            headers=headers,
        )
        return parse_cliq_response(payload)

    async def close(
        self,
        *,
        thread_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", f"/threads/{thread_id}/close", headers=headers)
        return parse_cliq_response(payload)

    async def reopen(
        self,
        *,
        thread_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request("POST", f"/threads/{thread_id}/reopen", headers=headers)
        return parse_cliq_response(payload)

    async def get_parent_message(
        self,
        *,
        thread_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> CliqResponse:
        payload = await self._cliq.request(
            "GET",
            f"/threads/{thread_id}/parentmessage",
            headers=headers,
        )
        return parse_cliq_response(payload)
