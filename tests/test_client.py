from __future__ import annotations

import pytest

from zoho.client import Zoho
from zoho.connections import ZohoConnectionProfile


def test_client_from_credentials_builds_settings() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        creator_environment_header="development",
        projects_default_portal_id="100",
        people_base_url="https://people.example.com",
        sheet_base_url="https://sheet.example.com",
        workdrive_base_url="https://workdrive.example.com",
        token_store_backend="memory",
    )

    assert client.settings.client_id == "cid"
    assert client.settings.token_store_backend == "memory"
    assert client.settings.creator_environment_header == "development"
    assert client.settings.projects_default_portal_id == "100"
    assert client.settings.people_base_url == "https://people.example.com"
    assert client.settings.sheet_base_url == "https://sheet.example.com"
    assert client.settings.workdrive_base_url == "https://workdrive.example.com"


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
    assert client.people is not None
    assert client.sheet is not None
    assert client.workdrive is not None


async def test_client_supports_manual_lifecycle_without_context_manager() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )

    assert client.closed is False
    await client.close()
    assert client.closed is True
    await client.aclose()


async def test_client_request_after_close_raises_helpful_error() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )
    await client.close()

    with pytest.raises(RuntimeError, match="client is closed"):
        await client._request_crm("GET", "/org")


async def test_closed_client_cannot_reenter_context_manager() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )
    await client.close()

    with pytest.raises(RuntimeError, match="client is closed"):
        async with client:
            pass


async def test_client_connection_manager_registration() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )
    profile = ZohoConnectionProfile(
        name="tenant_2",
        client_id="cid2",
        client_secret="secret2",
        refresh_token="refresh2",
        token_store_backend="memory",
    )
    client.register_connection(profile)

    names = client.connections.list()
    assert "default" in names
    assert "tenant_2" in names

    tenant_client = client.for_connection("tenant_2")
    assert tenant_client.settings.connection_name == "tenant_2"

    await client.close()
    assert tenant_client.closed is True
