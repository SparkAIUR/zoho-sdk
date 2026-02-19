# Authentication

## Required Credentials

The SDK uses Zoho OAuth refresh-token flow and requires:

- `client_id`
- `client_secret`
- `refresh_token`
- `dc` (`US`, `EU`, `IN`, `AU`, `JP`, `CA`, `SA`, `CN`)
- `environment` (`production`, `sandbox`, `developer`)

Optional product-specific settings:

- `creator_environment_header` (`development`, `stage`, `production`)
- `creator_base_url` (override Creator API host)
- `projects_default_portal_id` (omit repeated `portal_id` args for Projects calls)
- `projects_base_url` (override Projects API host)
- `people_base_url` (override People API host)
- `sheet_base_url` (override Sheet API host)
- `workdrive_base_url` (override WorkDrive API host)

## Credential Setup Guide

Use the dedicated step-by-step guide:

- [Credential Setup (Zoho OAuth)](auth-credentials.md)
- [Live Credential Validation (Admin)](admin-live-validation.md)

## SDK Initialization

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    environment="production",
    creator_environment_header="development",
    projects_default_portal_id="12345678",
)
```

Use either lifecycle style:

- `async with client` for one-shot scripts
- singleton + explicit `await client.close()` for long-lived services

See [Client Lifecycle](client-lifecycle.md) for patterns and shutdown examples.

## Multi-Account Profiles

```python
from zoho import ZohoConnectionProfile

client.register_connection(
    ZohoConnectionProfile(
        name="tenant_2",
        client_id="...",
        client_secret="...",
        refresh_token="...",
        dc="EU",
        people_base_url="https://people.zoho.eu",
    )
)

tenant_2 = client.for_connection("tenant_2")
```

Each connection profile has independent token caching namespace.

## Token Stores

- `memory`: in-memory only (tests, short-lived scripts)
- `sqlite` (default): persistent local cache
- `redis`: distributed worker scenarios

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    token_store_backend="redis",
    redis_url="redis://localhost:6379/0",
)
```

## Domain and Environment Correctness

Token cache keys include connection name + data center + environment.
This prevents cross-tenant and cross-region token reuse bugs.
