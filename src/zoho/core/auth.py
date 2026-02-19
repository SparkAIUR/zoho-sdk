"""OAuth2 refresh-token auth provider."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from zoho.core.errors import ZohoAuthError
from zoho.core.logging import get_logger
from zoho.core.token_store import OAuthToken, TokenStore

_ACCOUNTS_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://accounts.zoho.com",
    "EU": "https://accounts.zoho.eu",
    "IN": "https://accounts.zoho.in",
    "AU": "https://accounts.zoho.com.au",
    "JP": "https://accounts.zoho.jp",
    "CA": "https://accounts.zohocloud.ca",
    "SA": "https://accounts.zoho.sa",
    "CN": "https://accounts.zoho.com.cn",
}

_API_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://www.zohoapis.com",
    "EU": "https://www.zohoapis.eu",
    "IN": "https://www.zohoapis.in",
    "AU": "https://www.zohoapis.com.au",
    "JP": "https://www.zohoapis.jp",
    "CA": "https://www.zohocloud.ca",
    "SA": "https://www.zohoapis.sa",
    "CN": "https://www.zohoapis.com.cn",
}


class OAuth2RefreshAuthProvider:
    """Refresh-token OAuth provider with persisted token caching."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        dc: str,
        environment: str,
        token_store: TokenStore,
        accounts_domain: str | None = None,
        api_domain: str | None = None,
        cache_namespace: str = "default",
        user_agent: str = "zoho-sdk/0.1.1",
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._dc = dc
        self._environment = environment
        self._token_store = token_store
        self._accounts_domain = (accounts_domain or _ACCOUNTS_DOMAIN_BY_DC[dc]).rstrip("/")
        self._api_domain_override = api_domain
        self._user_agent = user_agent
        self._logger = get_logger("zoho.auth")

        self._http_client = http_client or httpx.AsyncClient(timeout=20.0)
        self._owns_http_client = http_client is None

        self._cache_key = f"{cache_namespace}:{client_id}:{dc}:{environment}:default"

    async def close(self) -> None:
        if self._owns_http_client:
            await self._http_client.aclose()

    async def get_auth_headers(self) -> dict[str, str]:
        token = await self.get_token()
        return {"Authorization": f"Zoho-oauthtoken {token.access_token}"}

    async def get_api_domain(self) -> str:
        if self._api_domain_override:
            return self._api_domain_override.rstrip("/")
        token = await self.get_token()
        if token.api_domain:
            return token.api_domain.rstrip("/")
        return _API_DOMAIN_BY_DC[self._dc]

    async def get_token(self) -> OAuthToken:
        existing = await self._token_store.load(self._cache_key)
        if existing and not existing.is_expired():
            return existing

        async with self._token_store.refresh_lock(self._cache_key):
            existing = await self._token_store.load(self._cache_key)
            if existing and not existing.is_expired():
                return existing

            refreshed = await self._refresh(existing)
            await self._token_store.save(self._cache_key, refreshed)
            return refreshed

    async def _refresh(self, existing: OAuthToken | None) -> OAuthToken:
        token_url = f"{self._accounts_domain}/oauth/v2/token"
        refresh_token = (
            existing.refresh_token
            if existing is not None and existing.refresh_token
            else self._refresh_token
        )

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }

        response = await self._http_client.post(
            token_url,
            data=payload,
            headers={"User-Agent": self._user_agent},
        )

        body: Mapping[str, Any]
        try:
            body = response.json()
        except ValueError:
            body = {}

        if response.status_code >= 400:
            raise ZohoAuthError(
                body.get("message", "Failed to refresh access token")
                if isinstance(body, Mapping)
                else "Failed to refresh access token",
                status_code=response.status_code,
                code=body.get("code") if isinstance(body, Mapping) else None,
                details=body if isinstance(body, Mapping) else None,
                method="POST",
                url=token_url,
                response_text=response.text[:500],
            )

        access_token = body.get("access_token") if isinstance(body, Mapping) else None
        if not isinstance(access_token, str) or not access_token:
            raise ZohoAuthError(
                "Token response did not include access_token",
                status_code=response.status_code,
                details=body if isinstance(body, Mapping) else None,
                method="POST",
                url=token_url,
            )

        expires_in_raw = body.get("expires_in_sec") if isinstance(body, Mapping) else None
        if expires_in_raw is None and isinstance(body, Mapping):
            expires_in_raw = body.get("expires_in")

        expires_in = int(expires_in_raw) if expires_in_raw is not None else 3600
        api_domain = body.get("api_domain") if isinstance(body, Mapping) else None
        scope_raw = body.get("scope") if isinstance(body, Mapping) else None
        scopes = tuple(str(scope_raw).split(",")) if scope_raw else ()

        token = OAuthToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(UTC) + timedelta(seconds=max(expires_in, 1)),
            api_domain=(
                str(api_domain) if api_domain else existing.api_domain if existing else None
            ),
            scope=scopes,
        )

        self._logger.info("oauth_token_refreshed", dc=self._dc, environment=self._environment)
        return token
