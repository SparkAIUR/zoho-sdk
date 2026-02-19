from __future__ import annotations

import os

import pytest

from zoho import Zoho
from zoho.people.models import PeopleResponse

_REQUIRED_ENV = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
)

pytestmark = pytest.mark.integration


async def test_people_forms_smoke() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing integration env vars: {', '.join(missing)}")

    client = Zoho.from_env()
    async with client:
        forms = await client.people.forms.list_forms()

    assert isinstance(forms, PeopleResponse)
