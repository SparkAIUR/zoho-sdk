# Getting Started

## Install

```bash
uv add zoho
```

## Recommended Initialization

Use explicit credentials for clarity and portability:

Need help obtaining credentials? See [Credential Setup (Zoho OAuth)](auth-credentials.md).

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    environment="production",
    creator_environment_header="development",  # optional
    projects_default_portal_id="12345678",     # optional
)
```

## First API Call

```python
async with client:
    org = await client.crm.org.get()
    print(org)
```

## Lifecycle Patterns

For one-shot scripts, prefer context manager usage (`async with`).

For long-lived web apps/workers, create one client and reuse it as a singleton. Close it at shutdown:

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

org = await client.crm.org.get()
await client.close()
```

See [Client Lifecycle](client-lifecycle.md) for FastAPI and singleton patterns.

## Creator and Projects Quick Calls

```python
async with client:
    forms = await client.creator.meta.get_forms(
        account_owner_name="owner",
        app_link_name="inventory_app",
    )
    print(forms.code, len(forms.data))

    projects = await client.projects.projects.list()
    if projects:
        print(projects[0].id, projects[0].name)
```

## Local Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy
```
