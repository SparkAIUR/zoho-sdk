from __future__ import annotations

import os

import pytest

from zoho import Zoho
from zoho.analytics.models import AnalyticsResponse

_REQUIRED_ENV = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
)

pytestmark = pytest.mark.integration


async def test_analytics_orgs_smoke() -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing integration env vars: {', '.join(missing)}")

    client = Zoho.from_env()
    async with client:
        orgs = await client.analytics.metadata.list_organizations()

    assert isinstance(orgs, AnalyticsResponse)
