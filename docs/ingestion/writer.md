# Writer Ingestion

`iter_writer_document_documents(...)` yields normalized `IngestionBatch` records from Writer document lists.

## Example

```python
from zoho.ingestion import iter_writer_document_documents

async for batch in iter_writer_document_documents(
    client,
    folder_id="folder_123",
    search="contract",
    page_size=200,
):
    for doc in batch.documents:
        print(doc.id, doc.title)
    print(batch.checkpoint)
```

## Checkpoint Semantics

- Uses `checkpoint.page` as the next page value.
- Stores `folder_id` and `search` in checkpoint extras.

This is useful for incremental document indexing in enterprise search pipelines.
