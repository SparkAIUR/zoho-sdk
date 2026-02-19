from __future__ import annotations

from zoho.client import Zoho


def test_client_from_credentials_builds_settings() -> None:
    client = Zoho.from_credentials(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        token_store_backend="memory",
    )

    assert client.settings.client_id == "cid"
    assert client.settings.token_store_backend == "memory"
