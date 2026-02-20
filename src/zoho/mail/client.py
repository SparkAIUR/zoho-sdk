"""Zoho Mail product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.mail.accounts import MailAccountsClient
    from zoho.mail.folders import MailFoldersClient
    from zoho.mail.messages import MailMessagesClient
    from zoho.mail.threads import MailThreadsClient


class MailRequestCallable(Protocol):
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


class MailClient:
    """Product-scoped Mail client."""

    def __init__(self, *, request: MailRequestCallable) -> None:
        self._request_fn = request
        self._accounts: MailAccountsClient | None = None
        self._folders: MailFoldersClient | None = None
        self._messages: MailMessagesClient | None = None
        self._threads: MailThreadsClient | None = None

    @property
    def accounts(self) -> MailAccountsClient:
        if self._accounts is None:
            from zoho.mail.accounts import MailAccountsClient

            self._accounts = MailAccountsClient(self)
        return self._accounts

    @property
    def folders(self) -> MailFoldersClient:
        if self._folders is None:
            from zoho.mail.folders import MailFoldersClient

            self._folders = MailFoldersClient(self)
        return self._folders

    @property
    def messages(self) -> MailMessagesClient:
        if self._messages is None:
            from zoho.mail.messages import MailMessagesClient

            self._messages = MailMessagesClient(self)
        return self._messages

    @property
    def threads(self) -> MailThreadsClient:
        if self._threads is None:
            from zoho.mail.threads import MailThreadsClient

            self._threads = MailThreadsClient(self)
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
