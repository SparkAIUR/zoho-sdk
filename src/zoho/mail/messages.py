"""Mail messages APIs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from zoho.mail.models import MailResponse, parse_mail_response

if TYPE_CHECKING:
    from zoho.mail.client import MailClient


class MailMessagesClient:
    """Message APIs for Zoho Mail."""

    def __init__(self, mail_client: MailClient) -> None:
        self._mail = mail_client

    async def list(
        self,
        *,
        account_id: str | int,
        folder_id: str | int | None = None,
        start: int | None = None,
        limit: int | None = None,
        status: str | None = None,
        thread_id: str | int | None = None,
        extra_params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        params: dict[str, Any] = {}
        if folder_id is not None:
            params["folderId"] = str(folder_id)
        if start is not None:
            params["start"] = start
        if limit is not None:
            params["limit"] = limit
        if status is not None:
            params["status"] = status
        if thread_id is not None:
            params["threadId"] = str(thread_id)
        if extra_params:
            params.update(extra_params)

        payload = await self._mail.request(
            "GET",
            f"/accounts/{account_id}/messages/view",
            params=params,
            headers=headers,
        )
        return parse_mail_response(payload)

    async def get(
        self,
        *,
        account_id: str | int,
        message_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "GET",
            f"/accounts/{account_id}/messages/{message_id}",
            headers=headers,
        )
        return parse_mail_response(payload)

    async def send(
        self,
        *,
        account_id: str | int,
        from_address: str,
        to: Sequence[str],
        subject: str,
        content: str,
        cc: Sequence[str] | None = None,
        bcc: Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload_data: dict[str, Any] = {
            "fromAddress": from_address,
            "toAddress": ",".join(to),
            "subject": subject,
            "content": content,
        }
        if cc:
            payload_data["ccAddress"] = ",".join(cc)
        if bcc:
            payload_data["bccAddress"] = ",".join(bcc)

        payload = await self._mail.request(
            "POST",
            f"/accounts/{account_id}/messages",
            json=payload_data,
            headers=headers,
        )
        return parse_mail_response(payload)

    async def move(
        self,
        *,
        account_id: str | int,
        message_id: str | int,
        folder_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "PUT",
            f"/accounts/{account_id}/messages/{message_id}/move",
            json={"folderId": str(folder_id)},
            headers=headers,
        )
        return parse_mail_response(payload)

    async def mark_read(
        self,
        *,
        account_id: str | int,
        message_id: str | int,
        is_read: bool = True,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "PUT",
            f"/accounts/{account_id}/messages/{message_id}",
            json={"isRead": is_read},
            headers=headers,
        )
        return parse_mail_response(payload)

    async def delete(
        self,
        *,
        account_id: str | int,
        message_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "DELETE",
            f"/accounts/{account_id}/messages/{message_id}",
            headers=headers,
        )
        return parse_mail_response(payload)
