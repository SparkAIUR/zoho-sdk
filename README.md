# zoho

Async-first Python SDK for Zoho, designed for developer experience and performance.

## Highlights

- Async-first transport built on `httpx`
- Explicit credential-first initialization (`from_credentials`)
- Strong typing with `pydantic` / `pydantic-settings`
- Pluggable token stores (memory, SQLite, Redis)
- Structlog-powered logging (`pretty` or `json`)
- Multi-account connection manager (`client.connections`)
- Product clients:
  - CRM (`records`, `modules`, `org`, `users`, `dynamic`)
  - Creator (`meta`, `data`, `publish`, `dynamic`)
  - Projects V3 (`portals`, `projects`, `tasks`)
  - People (`forms`, `employees`, `files`)
  - Sheet (`workbooks`, `worksheets`, `tabular`)
  - WorkDrive (`files`, `folders`, `search`, `changes`, `admin`)
- Ingestion iterators for connector workloads (`zoho.ingestion`)
- Codegen tooling + golden tests for spec drift

## Installation

```bash
uv add zoho
```

Optional extras:

```bash
uv add "zoho[redis]"      # Redis token store
uv add "zoho[orjson]"     # Faster JSON usage patterns
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
    ) as client:
        lead = await client.crm.records.get(module="Leads", record_id="123456789")
        print(lead.id)
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

Use a long-lived singleton for web apps/workers and close on shutdown:

```python
zoho_client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

project_rows = await zoho_client.projects.projects.list(portal_id="12345678")

# shutdown hook
await zoho_client.close()
```

After `close()`, `zoho_client.closed` is `True` and that instance must not be reused.

## Multi-Account Connections

```python
from zoho import Zoho, ZohoConnectionProfile

client = Zoho.from_credentials(
    client_id="primary_client_id",
    client_secret="primary_client_secret",
    refresh_token="primary_refresh_token",
)

client.register_connection(
    ZohoConnectionProfile(
        name="tenant_b",
        client_id="tenant_b_client_id",
        client_secret="tenant_b_client_secret",
        refresh_token="tenant_b_refresh_token",
        dc="EU",
        token_store_backend="sqlite",
    )
)

tenant_b = client.for_connection("tenant_b")
forms = await tenant_b.people.forms.list_forms()
print(forms.result_rows)
```

## Product Usage Examples

### People

```python
records = await client.people.forms.list_records(
    form_link_name="employee",
    limit=200,
)
print(records.result_rows)
```

### Sheet

```python
rows = await client.sheet.tabular.fetch_worksheet_records(
    workbook_id="workbook_123",
    worksheet_name="Data",
    limit=500,
)
print(rows.records)
```

### WorkDrive

```python
changes = await client.workdrive.changes.list_recent(
    folder_id="folder_123",
    limit=200,
)
print(changes.resources)
```

### CRM Dynamic Discovery

```python
if await client.crm.dynamic.has_module("Leads"):
    leads = client.crm.dynamic.Leads
    rows = await leads.list(page=1, per_page=200)
    print(rows.data)
```

### Creator Dynamic Discovery

```python
apps = await client.creator.dynamic.list_applications()
inventory = await client.creator.dynamic.get_application_client("owner.inventory-app")
forms = await inventory.meta.get_forms()
print(forms.data)
```

Precompile dynamic metadata for faster cold starts:

```python
await client.crm.dynamic.precompile_modules()
await client.creator.dynamic.precompile_applications()
```

## Ingestion Helpers (`pipeshub-ai`-friendly)

```python
from zoho.ingestion import iter_people_form_documents

async for batch in iter_people_form_documents(
    client,
    form_link_name="employee",
    connection_name="tenant_b",
    page_size=200,
):
    for doc in batch.documents:
        print(doc.id, doc.title)
    print(batch.checkpoint)
```

Additional iterators:
- `iter_crm_module_documents(...)`
- `iter_crm_documents(...)`
- `iter_sheet_worksheet_documents(...)`
- `iter_workdrive_recent_documents(...)`

## Getting OAuth Credentials

If you still need OAuth credentials, follow:
- `docs/auth-credentials.md`
- `docs/scopes.md`

At a high level:
1. Create a client in Zoho API Console.
2. Generate grant code(s) with required product scopes.
3. Exchange grant code for access/refresh tokens.
4. Use matching `dc` and accounts domain.

## Auth Helper CLI

Use the helper command for token exchange and self-client payload generation:

```bash
export ZOHO_CREDENTIALS_FILE=refs/notes/zoho-live.env
uv run zoho-auth exchange-token --grant-code "<grant-code>"

uv run zoho-auth grant-code \
  --self-client-id "1000..." \
  --scopes "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL,ZohoCRM.org.ALL"

uv run zoho-auth scope-builder \
  --product CRM \
  --product WorkDrive \
  --access read \
  --format env
```

See `docs/auth-cli.md` for execute mode and header/cookie options.

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

## Live Credential Validation (Admin)

Use the read-only validator before production rollout:

```bash
export ZOHO_CREDENTIALS_FILE=refs/notes/zoho-live.env
uv sync --group dev
uv run python tools/admin_validate_live.py
```

The script only runs read-oriented product checks and prints non-sensitive summaries
(counts/status only). See `docs/admin-live-validation.md` for required/optional vars.

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

### Creator summary

```bash
uv run python tools/codegen/creator_summary.py \
  --openapi tests/fixtures/creator_openapi_minimal.json \
  --output /tmp/creator_summary.json
```

### Projects extraction

```bash
uv run python tools/codegen/projects_extract.py \
  --html tests/fixtures/projects/api_docs_sample.html \
  --output /tmp/projects_mvp.json
```

### Curated product specs summary (People/Sheet/WorkDrive)

```bash
uv run python tools/codegen/curated_summary.py \
  --spec tools/specs/people_v1_curated.json \
  --spec tools/specs/sheet_v2_curated.json \
  --spec tools/specs/workdrive_v1_curated.json \
  --output /tmp/curated_summary.json
```

## Repository Docs

- Product docs: `docs/`
- Use-case playbooks: `docs/use-cases/`
- API research notes: `refs/apis/`
- Design specs: `refs/docs/specs/`
- Contributor guide: `AGENTS.md`
