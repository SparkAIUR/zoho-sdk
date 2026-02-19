from __future__ import annotations

import os

import pytest

from zoho import Zoho

_REQUIRED_ENV = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
    "ZOHO_PROJECTS_PORTAL_ID",
)

pytestmark = pytest.mark.integration


async def test_projects_list_smoke() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing integration env vars: {', '.join(missing)}")

    client = Zoho.from_env()
    async with client:
        projects = await client.projects.projects.list(
            portal_id=os.environ["ZOHO_PROJECTS_PORTAL_ID"]
        )

    assert isinstance(projects, list)
