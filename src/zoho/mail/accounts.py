"""Mail accounts APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from zoho.mail.models import MailResponse, parse_mail_response

if TYPE_CHECKING:
    from zoho.mail.client import MailClient


class MailAccountsClient:
    """Account APIs for Zoho Mail."""

    def __init__(self, mail_client: MailClient) -> None:
        self._mail = mail_client

    async def list(self, *, headers: Mapping[str, str] | None = None) -> MailResponse:
        payload = await self._mail.request("GET", "/accounts", headers=headers)
        return parse_mail_response(payload)

    async def get(
        self,
        *,
        account_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> MailResponse:
        payload = await self._mail.request("GET", f"/accounts/{account_id}", headers=headers)
        return parse_mail_response(payload)
