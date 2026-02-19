# Ingestion Helpers

`zoho.ingestion` provides normalized async iterators for connector workloads.

## Why Use These Helpers

- stable document shape for indexing pipelines
- resumable checkpoints (`offset` and `cursor`)
- tenant routing via `connection_name`

## People Form Iterator

```python
from zoho.ingestion import iter_people_form_documents

async for batch in iter_people_form_documents(
    client,
    form_link_name="employee",
    page_size=200,
):
    for doc in batch.documents:
        print(doc.id, doc.title)
```

## Sheet Worksheet Iterator

```python
from zoho.ingestion import iter_sheet_worksheet_documents

async for batch in iter_sheet_worksheet_documents(
    client,
    workbook_id="workbook_123",
    worksheet_name="Data",
    connection_name="tenant_2",
):
    print(batch.checkpoint)
```

## WorkDrive Recent Changes Iterator

```python
from zoho.ingestion import iter_workdrive_recent_documents

async for batch in iter_workdrive_recent_documents(
    client,
    folder_id="folder_123",
):
    print(len(batch.documents), batch.checkpoint)
```
