# zoho

Async-first Python SDK for Zoho, designed for developer experience and performance.

## Highlights

- Async-first transport built on `httpx`
- Explicit credential-first initialization (`from_credentials`)
- Strong typing with `pydantic` / `pydantic-settings`
- Pluggable token stores (memory, SQLite, Redis)
- Structlog-powered logging (`pretty` or `json`)
- CRM APIs (`records`, `modules`, `org`, `users`)
- Creator APIs (`meta`, `data`, `publish`)
- Projects V3 APIs (`portals`, `projects`, `tasks`)
- Codegen tooling + golden tests for spec drift

## Installation

```bash
uv add zoho
```

Optional extras:

```bash
uv add "zoho[redis]"      # Redis token store
uv add "zoho[orjson]"     # Faster JSON rendering usage patterns
```

## Quick Start (Explicit Credentials)

```python
from zoho import Zoho

async def main() -> None:
    async with Zoho.from_credentials(
        client_id="your_client_id",
        client_secret="your_client_secret",
        refresh_token="your_refresh_token",
        dc="US",
        environment="production",
        token_store_backend="sqlite",
    ) as client:
        lead = await client.crm.records.get(module="Leads", record_id="123456789")
        print(lead.id, lead.get("Last_Name"))
```

## Client Lifecycle: Context Manager vs Singleton

Both patterns are supported.

Use `async with` for one-shot scripts/jobs:

```python
async with Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
) as client:
    org = await client.crm.org.get()
```

Use a long-lived singleton for web apps/workers and close at shutdown:

```python
zoho_client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

lead = await zoho_client.crm.records.get(module="Leads", record_id="123456789")

# app shutdown hook
await zoho_client.close()
```

After `close()`, `zoho_client.closed` becomes `True` and that instance should not be reused.

## Product Usage Examples

### CRM

```python
async for record in client.crm.records.iter(
    module="Leads",
    per_page=200,
    fields=["Email", "Last_Name"],
):
    print(record.get("Email"))
```

### Creator

```python
forms = await client.creator.meta.get_forms(
    account_owner_name="owner",
    app_link_name="inventory_app",
)
print(forms.code, len(forms.data))
```

### Projects

```python
projects = await client.projects.projects.list(portal_id="12345678")
if projects:
    print(projects[0].id, projects[0].name)
```

## Getting Zoho Credentials (client_id/client_secret/refresh_token)

If you still need OAuth credentials, follow:

- `docs/auth-credentials.md` (full step-by-step)

At a high level:
1. Create a client in Zoho API Console (Self Client for quick backend setup).
2. Generate a grant code with CRM scopes.
3. Exchange the grant code for tokens and keep `refresh_token`.
4. Use matching data center (`dc`) and accounts domain.

## Environment-Based Setup (Convenience)

```bash
export ZOHO_CLIENT_ID="..."
export ZOHO_CLIENT_SECRET="..."
export ZOHO_REFRESH_TOKEN="..."
export ZOHO_DC="US"
export ZOHO_ENVIRONMENT="production"
```

```python
from zoho import Zoho

async with Zoho.from_env() as client:
    org = await client.crm.org.get()
    print(org)
```

## High-Usage Workflows

### Create and update CRM records

```python
created = await client.crm.records.create(
    module="Leads",
    data={"Last_Name": "Ng", "Company": "Acme"},
)

await client.crm.records.update(
    module="Leads",
    record_id="123456789",
    data={"Last_Name": "Chen"},
)
```

### Cache CRM module metadata lookups

```python
modules = await client.crm.modules.list(use_cache=True, cache_ttl_seconds=3600)
lead_module = await client.crm.modules.get("Leads", use_cache=True)
```

### Use Creator environment header + Projects default portal

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    creator_environment_header="development",
    projects_default_portal_id="12345678",
)
```

## Logging Modes

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    log_format="json",   # "pretty" for colored local logs
)
```

## Development

```bash
uv sync --group dev
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run mkdocs build --strict
```

## Codegen Workflows

### CRM summary

```bash
uv run python tools/codegen/main.py \
  --json-details tests/fixtures/json_details_minimal.json \
  --openapi tests/fixtures/openapi_minimal.json \
  --output /tmp/zoho_ir_summary.json
```

### Creator endpoint summary

```bash
uv run python tools/codegen/creator_summary.py \
  --openapi tests/fixtures/creator_openapi_minimal.json \
  --output /tmp/creator_summary.json
```

### Projects docs extraction (fixture or live docs)

```bash
# from fixture
uv run python tools/codegen/projects_extract.py \
  --html tests/fixtures/projects/api_docs_sample.html \
  --output /tmp/projects_mvp.json

# from live docs (network)
uv run python tools/codegen/projects_extract.py \
  --all \
  --output tools/specs/projects_v3_extracted.json
```

## Repository Docs

- Product/user docs: `docs/`
- Design specs: `refs/docs/specs/`
- Contributor guide: `AGENTS.md`
