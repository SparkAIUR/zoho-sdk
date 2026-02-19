"""FastAPI backend for tenant/user Zoho OAuth grant handling."""

from __future__ import annotations

import secrets
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


# --8<-- [start:oauth_settings]
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ZOHO_", extra="ignore")

    client_id: str
    client_secret: str
    redirect_uri: str
    scopes_csv: str
    accounts_domain: str = "https://accounts.zoho.com"
    app_base_url: str = "http://localhost:3000"


settings = Settings()
app = FastAPI(title="Zoho OAuth Backend")
# --8<-- [end:oauth_settings]


class OAuthState(BaseModel):
    tenant_id: str
    nonce: str


class TenantToken(BaseModel):
    tenant_id: str
    access_token: str
    refresh_token: str
    api_domain: str | None = None


oauth_states: dict[str, OAuthState] = {}
tenant_tokens: dict[str, TenantToken] = {}


# --8<-- [start:oauth_start]
@app.get("/oauth/{tenant_id}/start")
async def oauth_start(tenant_id: str) -> dict[str, str]:
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    oauth_states[state] = OAuthState(tenant_id=tenant_id, nonce=nonce)

    params = {
        "response_type": "code",
        "client_id": settings.client_id,
        "scope": settings.scopes_csv,
        "redirect_uri": settings.redirect_uri,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    authorize_url = f"{settings.accounts_domain}/oauth/v2/auth?{urlencode(params)}"
    return {"authorize_url": authorize_url}
# --8<-- [end:oauth_start]


# --8<-- [start:oauth_callback]
@app.get("/oauth/callback")
async def oauth_callback(
    code: str = Query(min_length=1),
    state: str = Query(min_length=1),
) -> dict[str, Any]:
    state_payload = oauth_states.pop(state, None)
    if state_payload is None:
        raise HTTPException(status_code=400, detail="invalid_state")

    token_url = f"{settings.accounts_domain}/oauth/v2/token"
    token_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "redirect_uri": settings.redirect_uri,
    }

    async with httpx.AsyncClient(timeout=30.0) as http:
        response = await http.post(token_url, data=token_payload)
    response.raise_for_status()

    token_data = response.json()
    refresh_token = token_data.get("refresh_token")
    access_token = token_data.get("access_token")

    if not isinstance(refresh_token, str) or not isinstance(access_token, str):
        raise HTTPException(status_code=400, detail="missing_tokens")

    tenant_token = TenantToken(
        tenant_id=state_payload.tenant_id,
        access_token=access_token,
        refresh_token=refresh_token,
        api_domain=(token_data.get("api_domain") if isinstance(token_data, dict) else None),
    )
    tenant_tokens[state_payload.tenant_id] = tenant_token

    return {
        "tenant_id": state_payload.tenant_id,
        "status": "connected",
        "api_domain": tenant_token.api_domain,
    }
# --8<-- [end:oauth_callback]


# --8<-- [start:tenant_token_lookup]
@app.get("/oauth/{tenant_id}/token")
async def oauth_token_status(tenant_id: str) -> dict[str, Any]:
    """Returns non-sensitive tenant token status for admin dashboards."""

    token = tenant_tokens.get(tenant_id)
    return {
        "tenant_id": tenant_id,
        "connected": token is not None,
        "api_domain": token.api_domain if token is not None else None,
    }
# --8<-- [end:tenant_token_lookup]
