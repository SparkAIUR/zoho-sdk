# Ingestion Helpers

`zoho.ingestion` provides normalized async iterators for connector workloads.

## Why Use These Helpers

- stable document shape for indexing pipelines
- resumable checkpoints (`offset` and `cursor`)
- tenant routing via `connection_name`
- metadata-safe defaults (no raw/content unless explicitly enabled)

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

## CRM Module Iterator

```python
from zoho.ingestion import iter_crm_module_documents

async for batch in iter_crm_module_documents(
    client,
    module="Leads",
    page_size=200,
):
    print(batch.checkpoint, len(batch.documents))
```

## Mail Messages Iterator

```python
from zoho.ingestion import iter_mail_message_documents

async for batch in iter_mail_message_documents(
    client,
    account_id="123456789",
    folder_id="100",
    page_size=200,
):
    print(batch.checkpoint, len(batch.documents))
```

## Writer Documents Iterator

```python
from zoho.ingestion import iter_writer_document_documents

async for batch in iter_writer_document_documents(
    client,
    folder_id="folder_123",
    page_size=200,
):
    print(batch.checkpoint, len(batch.documents))
```

## Cliq Ingestion Workflow

```python
--8<-- "examples/ingestion/cliq_pipeline.py:channel_chat_job"
```

```python
--8<-- "examples/ingestion/cliq_pipeline.py:thread_job"
```

## Analytics Ingestion Workflow

```python
--8<-- "examples/ingestion/analytics_pipeline.py:workspace_graph_job"
```

```python
--8<-- "examples/ingestion/analytics_pipeline.py:view_rows_job"
```
