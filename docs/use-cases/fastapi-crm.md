# FastAPI Server-Side Application

This pattern is for API backends that need shared Zoho client lifecycle management and dynamic CRM module access.

## Target Use Case

- Single FastAPI service handling many CRM endpoints.
- Optional multi-tenant routing via named Zoho connections.
- Runtime module flexibility with `client.crm.dynamic`.

## Required Scopes (minimum baseline)

- `ZohoCRM.modules.READ`
- `ZohoCRM.settings.READ`
- `ZohoCRM.users.READ`
- `ZohoCRM.org.READ`

## App Settings

```python
--8<-- "examples/fastapi_crm/main.py:settings"
```

## Singleton Client Lifecycle

```python
--8<-- "examples/fastapi_crm/main.py:lifespan"
```

## Tenant-Aware Client Dependency

```python
--8<-- "examples/fastapi_crm/main.py:tenant_dependency"
```

## CRM Submodule Endpoint (Dynamic Discovery)

```python
--8<-- "examples/fastapi_crm/main.py:crm_dynamic_endpoint"
```

## Notes

- Prefer one client per process and close once on shutdown.
- Register additional tenant connections at startup, not per request.
- Use dynamic discovery for flexible module coverage; use static subclients for fixed workflows.
