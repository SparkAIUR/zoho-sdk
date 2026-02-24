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
  - CRM (`records`, `coql`, `modules`, `org`, `users`, `dynamic`)
  - Creator (`meta`, `data`, `publish`, `dynamic`)
  - Projects V3 (`portals`, `projects`, `tasks`)
  - People (`forms`, `employees`, `files`)
  - Sheet (`workbooks`, `worksheets`, `tabular`)
  - WorkDrive (`files`, `folders`, `search`, `changes`, `admin`)
  - Cliq (`users`, `chats`, `channels`, `messages`, `threads`)
  - Analytics (`metadata`, `data`, `bulk`)
  - Writer (`documents`, `folders`, `merge`)
  - Mail (`accounts`, `folders`, `messages`, `threads`)
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

### Cliq

```python
channels = await client.cliq.channels.list(limit=50)
print(channels.result_rows)
```

### Analytics

```python
orgs = await client.analytics.metadata.list_organizations()
print(orgs.result_rows)
```

### Writer

```python
documents = await client.writer.documents.list(limit=20)
print(documents.result_rows)
```

### Mail

```python
accounts = await client.mail.accounts.list()
print(accounts.result_rows)
```

### CRM COQL

```python
result = await client.crm.coql.execute(
    query=(
        "select Signers.Email, Signers.Phone "
        "from Deals_X_Contacts where Signer_Deals.Loan_ID = :loan_id"
    ),
    params={"loan_id": "xxx"},
)
print(result.data)
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

```python
from zoho.ingestion import iter_cliq_chat_documents

async for batch in iter_cliq_chat_documents(
    client,
    include_messages=True,
    page_size=200,
):
    for doc in batch.documents:
        print(doc.source, doc.id)
```

```python
from zoho.ingestion import iter_analytics_view_documents

async for batch in iter_analytics_view_documents(
    client,
    workspace_id="workspace_123",
    view_id="view_123",
    strategy="bulk",  # or "direct"
    headers={"ZANALYTICS-ORGID": "123456789"},
):
    print(batch.checkpoint, len(batch.documents))
```

Additional iterators:
- `iter_crm_module_documents(...)`
- `iter_crm_documents(...)`
- `iter_cliq_channel_documents(...)`
- `iter_cliq_chat_documents(...)`
- `iter_cliq_thread_documents(...)`
- `iter_analytics_workspace_documents(...)`
- `iter_analytics_view_documents(...)`
- `iter_sheet_worksheet_documents(...)`
- `iter_workdrive_recent_documents(...)`
- `iter_mail_message_documents(...)`
- `iter_writer_document_documents(...)`

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
  --product Mail \
  --product Writer \
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

## Security Scan (Pre-Public / Pre-Release)

Run the high-confidence scanner against tracked files and full git history:

```bash
uv run python tools/security_scan.py --mode all --report .security/secrets-report.json
```

If findings are detected, rotate/revoke affected credentials and clean files/history
before publishing. See `SECURITY.md` for the response process.

## Development

```bash
uv sync --group dev
git clone https://github.com/SparkAIUR/sparkify.git .sparkify-tool
(cd .sparkify-tool && npm ci && npm run build)
export DOCS_SITE_URL="https://docs.example.com"
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run pytest tests/tools/test_render_sparkify_docs.py
uv run python tools/render_sparkify_docs.py \
  --source docs \
  --output .sparkify/docs \
  --mkdocs-config mkdocs.yml
(cd .sparkify-tool && node packages/cli/dist/bin.js build \
  --docs-dir ../.sparkify/docs \
  --out ../.sparkify/site \
  --site "${DOCS_SITE_URL}" \
  --base "" \
  --strict)
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

## Docs Deployment Variables

Set these repository variables for CI/docs deployment:

- `DOCS_SITE_URL` (required): canonical docs origin, for example `https://docs.example.com`
- `DOCS_CUSTOM_DOMAIN` (optional): hostname written to `site/CNAME` for Pages custom domains
- `SPARKIFY_REF` (required): pinned branch or commit SHA used to checkout `SparkAIUR/sparkify`

When upgrading Sparkify in CI, update `SPARKIFY_REF` first in repository variables, then re-run the docs workflow.
