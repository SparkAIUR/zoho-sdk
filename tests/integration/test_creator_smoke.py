from __future__ import annotations

import os

import pytest

from zoho import Zoho
from zoho.creator.models import CreatorResponse

_REQUIRED_ENV = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
    "ZOHO_CREATOR_ACCOUNT_OWNER",
    "ZOHO_CREATOR_APP_LINK_NAME",
    "ZOHO_CREATOR_FORM_LINK_NAME",
)

pytestmark = pytest.mark.integration


async def test_creator_meta_smoke() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing integration env vars: {', '.join(missing)}")

    client = Zoho.from_env()
    async with client:
        fields = await client.creator.meta.get_form_fields(
            account_owner_name=os.environ["ZOHO_CREATOR_ACCOUNT_OWNER"],
            app_link_name=os.environ["ZOHO_CREATOR_APP_LINK_NAME"],
            form_link_name=os.environ["ZOHO_CREATOR_FORM_LINK_NAME"],
        )

    assert isinstance(fields, CreatorResponse)
