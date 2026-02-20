"""Zoho Cliq product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.cliq.channels import CliqChannelsClient
    from zoho.cliq.chats import CliqChatsClient
    from zoho.cliq.messages import CliqMessagesClient
    from zoho.cliq.threads import CliqThreadsClient
    from zoho.cliq.users import CliqUsersClient


class CliqRequestCallable(Protocol):
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


class CliqClient:
    """Product-scoped Cliq client."""

    def __init__(self, *, request: CliqRequestCallable) -> None:
        self._request_fn = request
        self._users: CliqUsersClient | None = None
        self._chats: CliqChatsClient | None = None
        self._channels: CliqChannelsClient | None = None
        self._messages: CliqMessagesClient | None = None
        self._threads: CliqThreadsClient | None = None

    @property
    def users(self) -> CliqUsersClient:
        if self._users is None:
            from zoho.cliq.users import CliqUsersClient

            self._users = CliqUsersClient(self)
        return self._users

    @property
    def chats(self) -> CliqChatsClient:
        if self._chats is None:
            from zoho.cliq.chats import CliqChatsClient

            self._chats = CliqChatsClient(self)
        return self._chats

    @property
    def channels(self) -> CliqChannelsClient:
        if self._channels is None:
            from zoho.cliq.channels import CliqChannelsClient

            self._channels = CliqChannelsClient(self)
        return self._channels

    @property
    def messages(self) -> CliqMessagesClient:
        if self._messages is None:
            from zoho.cliq.messages import CliqMessagesClient

            self._messages = CliqMessagesClient(self)
        return self._messages

    @property
    def threads(self) -> CliqThreadsClient:
        if self._threads is None:
            from zoho.cliq.threads import CliqThreadsClient

            self._threads = CliqThreadsClient(self)
        return self._threads

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
