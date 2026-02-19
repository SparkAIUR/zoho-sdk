# CRM Ingestion

`zoho.ingestion` includes CRM-first iterators designed for enterprise search connectors.

## Module Iterator

Use `iter_crm_module_documents` to crawl one CRM module with resumable checkpoints.

```python
from zoho.ingestion import iter_crm_module_documents

async for batch in iter_crm_module_documents(
    client,
    module="Leads",
    fields=["id", "Full_Name", "Modified_Time"],
    page_size=200,
):
    print(batch.checkpoint, len(batch.documents))
```

## Multi-Module Iterator

Use `iter_crm_documents` when you want one stream across an explicit module allowlist.

```python
from zoho.ingestion import iter_crm_documents

async for batch in iter_crm_documents(
    client,
    modules=["Leads", "Contacts", "Accounts"],
    page_size=200,
):
    for doc in batch.documents:
        print(doc.id, doc.metadata["module"])
```

## Checkpoint Model

- Per-module crawl checkpoint includes `page`.
- Multi-module crawl checkpoint includes:
  - `extras.module_name`
  - `extras.module_index`

Persist checkpoints between connector runs to support resumable indexing.
