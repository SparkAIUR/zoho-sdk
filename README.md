# zoho

Async-first Python SDK for Zoho, designed for developer experience and performance.

## Highlights

- Async-first transport built on `httpx`
- Explicit credential-first initialization (`from_credentials`)
- Strong typing with `pydantic` / `pydantic-settings`
- Pluggable token stores (memory, SQLite, Redis)
- Structlog-powered logging (`pretty` or `json`)
- CRM foundation APIs (records, modules, org, users)
- Codegen scaffolding with golden tests for spec drift

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

## CRM Usage Examples

### Iterate records efficiently

```python
async for record in client.crm.records.iter(
    module="Leads",
    per_page=200,
    fields=["Email", "Last_Name"],
):
    print(record.get("Email"))
```

### Create and update records

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

### Cache module metadata lookups

```python
modules = await client.crm.modules.list(use_cache=True, cache_ttl_seconds=3600)
lead_module = await client.crm.modules.get("Leads", use_cache=True)
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

## Codegen (v0.0.1 scaffolding)

```bash
uv run python tools/codegen/main.py \
  --json-details tests/fixtures/json_details_minimal.json \
  --openapi tests/fixtures/openapi_minimal.json \
  --output /tmp/zoho_ir_summary.json
```

## Repository Docs

- Product/user docs: `docs/`
- Design specs: `refs/docs/specs/`
- Contributor guide: `AGENTS.md`
