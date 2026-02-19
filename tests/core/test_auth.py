from __future__ import annotations

import httpx
import respx

from zoho.core.auth import OAuth2RefreshAuthProvider
from zoho.core.token_store import MemoryTokenStore


async def test_auth_provider_refreshes_and_caches() -> None:
    store = MemoryTokenStore()
    http_client = httpx.AsyncClient()

    provider = OAuth2RefreshAuthProvider(
        client_id="cid",
        client_secret="secret",
        refresh_token="refresh",
        dc="US",
        environment="production",
        token_store=store,
        http_client=http_client,
    )

    with respx.mock(assert_all_called=True) as router:
        route = router.post("https://accounts.zoho.com/oauth/v2/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "token-1",
                    "expires_in_sec": 3600,
                    "api_domain": "https://www.zohoapis.com",
                },
            )
        )

        headers_1 = await provider.get_auth_headers()
        headers_2 = await provider.get_auth_headers()

    assert route.call_count == 1
    assert headers_1["Authorization"] == "Zoho-oauthtoken token-1"
    assert headers_2["Authorization"] == "Zoho-oauthtoken token-1"

    await http_client.aclose()
