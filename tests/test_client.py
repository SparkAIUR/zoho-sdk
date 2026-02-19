from __future__ import annotations

from zoho.client import Zoho


def test_client_from_credentials_builds_settings() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        creator_environment_header="development",
        projects_default_portal_id="100",
        token_store_backend="memory",
    )

    assert client.settings.client_id == "cid"
    assert client.settings.token_store_backend == "memory"
    assert client.settings.creator_environment_header == "development"
    assert client.settings.projects_default_portal_id == "100"


def test_client_lazy_products_are_available() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )

    assert client.crm is not None
    assert client.creator is not None
    assert client.projects is not None
