# Writer Overview

`client.writer` provides document, folder, and merge APIs for Zoho Writer.

## Quick Example

```python
documents = await client.writer.documents.list(limit=50)
for doc in documents.result_rows:
    print(doc.get("title"), doc.get("id"))
```

## Scope Notes

Core scopes often include:
- `ZohoWriter.documentEditor.ALL`
- `ZohoWriter.merge.ALL`

Some workflows may additionally need WorkDrive or ZohoPC scopes.
