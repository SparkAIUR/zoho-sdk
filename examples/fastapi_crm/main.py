"""FastAPI + Zoho CRM example with tenant-aware dynamic module access."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from zoho import Zoho, ZohoConnectionProfile


# --8<-- [start:settings]
class Settings(BaseSettings):
    """Environment-driven runtime settings for the API server."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ZOHO_", extra="ignore")

    client_id: str
    client_secret: str
    refresh_token: str
    dc: str = "US"

    tenant_eu_client_id: str | None = None
    tenant_eu_client_secret: str | None = None
    tenant_eu_refresh_token: str | None = None


settings = Settings()
# --8<-- [end:settings]


# --8<-- [start:lifespan]
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create one shared Zoho client for the process and close it on shutdown."""

    app.state.zoho = Zoho.from_credentials(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        refresh_token=settings.refresh_token,
        dc=settings.dc,
    )

    if (
        settings.tenant_eu_client_id
        and settings.tenant_eu_client_secret
        and settings.tenant_eu_refresh_token
    ):
        app.state.zoho.register_connection(
            ZohoConnectionProfile(
                name="tenant_eu",
                client_id=settings.tenant_eu_client_id,
                client_secret=settings.tenant_eu_client_secret,
                refresh_token=settings.tenant_eu_refresh_token,
                dc="EU",
            )
        )

    yield

    await app.state.zoho.close()


app = FastAPI(title="Zoho CRM API", lifespan=lifespan)
# --8<-- [end:lifespan]


# --8<-- [start:tenant_dependency]
def resolve_tenant_client(
    request: Request,
    tenant: Annotated[str, Query(description="Connection name", min_length=1)] = "default",
) -> Zoho:
    root_client: Zoho = request.app.state.zoho

    if tenant == "default":
        return root_client

    try:
        return root_client.for_connection(tenant)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown tenant connection: {tenant}") from exc


TenantClient = Annotated[Zoho, Depends(resolve_tenant_client)]
# --8<-- [end:tenant_dependency]


class CRMListResponse(BaseModel):
    module: str
    page: int
    count: int
    records: list[dict[str, Any]]


# --8<-- [start:crm_dynamic_endpoint]
@app.get("/crm/{module_name}", response_model=CRMListResponse)
async def list_crm_module_records(
    module_name: str,
    client: TenantClient,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=200)] = 200,
    fields: Annotated[list[str] | None, Query()] = None,
) -> CRMListResponse:
    """Use CRM dynamic discovery to support any enabled module at runtime."""

    module_client = await client.crm.dynamic.get_module_client(module_name)
    result = await module_client.list(page=page, per_page=per_page, fields=fields)

    return CRMListResponse(
        module=module_client.module_api_name,
        page=page,
        count=len(result.data),
        records=result.data,
    )
# --8<-- [end:crm_dynamic_endpoint]
