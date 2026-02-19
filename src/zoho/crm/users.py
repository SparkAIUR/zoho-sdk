"""CRM Users operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient

UserListType = Literal[
    "AllUsers",
    "ActiveUsers",
    "DeactiveUsers",
    "ConfirmedUsers",
    "NotConfirmedUsers",
    "DeletedUsers",
    "ActiveConfirmedUsers",
    "AdminUsers",
    "ActiveConfirmedAdmins",
    "CurrentUser",
]


class UsersClient:
    """CRM users endpoints."""

    def __init__(self, crm_client: CRMClient) -> None:
        self._crm = crm_client

    async def list(
        self,
        *,
        user_type: UserListType = "ActiveUsers",
        page: int = 1,
        per_page: int = 200,
    ) -> list[dict[str, Any]]:
        payload = await self._crm.request(
            "GET",
            "/users",
            params={"type": user_type, "page": page, "per_page": per_page},
        )
        users = payload.get("users")
        return [item for item in users if isinstance(item, dict)] if isinstance(users, list) else []
