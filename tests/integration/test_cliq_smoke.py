from __future__ import annotations

import os

import pytest

from zoho import Zoho
from zoho.cliq.models import CliqResponse

_REQUIRED_ENV = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
)

pytestmark = pytest.mark.integration


async def test_cliq_users_smoke() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing integration env vars: {', '.join(missing)}")

    client = Zoho.from_env()
    async with client:
        users = await client.cliq.users.list(limit=10)

    assert isinstance(users, CliqResponse)
