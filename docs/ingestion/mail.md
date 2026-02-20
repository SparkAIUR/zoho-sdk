# Mail Ingestion

`iter_mail_message_documents(...)` yields normalized `IngestionBatch` objects from Zoho Mail message lists.

## Example

```python
from zoho.ingestion import iter_mail_message_documents

async for batch in iter_mail_message_documents(
    client,
    account_id="123456789",
    folder_id="100",
    connection_name="tenant_b",
    page_size=200,
):
    for doc in batch.documents:
        print(doc.id, doc.title)
    print(batch.checkpoint)
```

## Checkpoint Semantics

- Uses `checkpoint.offset` as the next `start` sequence value.
- Stores `account_id` and `folder_id` in checkpoint extras.

This pattern is suitable for resumable enterprise email ingestion.
