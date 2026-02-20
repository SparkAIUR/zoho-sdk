"""Mail folders APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.mail.models import MailResponse, parse_mail_response

if TYPE_CHECKING:
    from zoho.mail.client import MailClient


class MailFoldersClient:
    """Folder APIs for Zoho Mail."""

    def __init__(self, mail_client: MailClient) -> None:
        self._mail = mail_client

    async def list(
        self,
        *,
        account_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "GET", f"/accounts/{account_id}/folders", headers=headers
        )
        return parse_mail_response(payload)

    async def get(
        self,
        *,
        account_id: str | int,
        folder_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "GET",
            f"/accounts/{account_id}/folders/{folder_id}",
            headers=headers,
        )
        return parse_mail_response(payload)

    async def create(
        self,
        *,
        account_id: str | int,
        folder_name: str,
        parent_folder_id: str | int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        data: dict[str, Any] = {"folderName": folder_name}
        if parent_folder_id is not None:
            data["parentFolderId"] = str(parent_folder_id)

        payload = await self._mail.request(
            "POST",
            f"/accounts/{account_id}/folders",
            json=data,
            headers=headers,
        )
        return parse_mail_response(payload)

    async def update(
        self,
        *,
        account_id: str | int,
        folder_id: str | int,
        folder_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "PUT",
            f"/accounts/{account_id}/folders/{folder_id}",
            json={"folderName": folder_name},
            headers=headers,
        )
        return parse_mail_response(payload)

    async def delete(
        self,
        *,
        account_id: str | int,
        folder_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request(
            "DELETE",
            f"/accounts/{account_id}/folders/{folder_id}",
            headers=headers,
        )
        return parse_mail_response(payload)
