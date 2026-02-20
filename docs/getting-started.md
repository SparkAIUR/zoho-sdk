# Getting Started

## Install

```bash
uv add zoho
```

## Recommended Initialization

Use explicit credentials for clarity and portability.

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

## Multi-Account Setup

```python
from zoho import ZohoConnectionProfile

client.register_connection(
    ZohoConnectionProfile(
        name="tenant_2",
        client_id="...",
        client_secret="...",
        refresh_token="...",
        dc="EU",
    )
)

tenant_2 = client.for_connection("tenant_2")
forms = await tenant_2.people.forms.list_forms()
```

## Product Quick Calls

```python
async with client:
    people_forms = await client.people.forms.list_forms()
    sheet_rows = await client.sheet.tabular.fetch_worksheet_records(
        workbook_id="workbook_123",
        worksheet_name="Data",
    )
    workdrive_changes = await client.workdrive.changes.list_recent(folder_id="folder_123")
    channels = await client.cliq.channels.list(limit=20)
    analytics_orgs = await client.analytics.metadata.list_organizations()
    writer_docs = await client.writer.documents.list(limit=20)
    mail_accounts = await client.mail.accounts.list()

    print(people_forms.result_rows)
    print(sheet_rows.records)
    print(workdrive_changes.resources)
    print(channels.result_rows)
    print(analytics_orgs.result_rows)
    print(writer_docs.result_rows)
    print(mail_accounts.result_rows)
```

## Ingestion Quick Call

```python
from zoho.ingestion import (
    iter_mail_message_documents,
    iter_workdrive_recent_documents,
    iter_writer_document_documents,
)

async for batch in iter_workdrive_recent_documents(client, folder_id="folder_123"):
    print(batch.checkpoint, len(batch.documents))

async for batch in iter_mail_message_documents(client, account_id="123456789", folder_id="100"):
    print(batch.checkpoint, len(batch.documents))

async for batch in iter_writer_document_documents(client, folder_id="folder_123"):
    print(batch.checkpoint, len(batch.documents))
```

## Local Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy
```
