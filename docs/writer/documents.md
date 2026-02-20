# Writer Documents API

```python
docs = await client.writer.documents.list(limit=100)
doc = await client.writer.documents.get(document_id="doc_id")
```

CRUD and export:

```python
created = await client.writer.documents.create(title="Q2 Plan")
await client.writer.documents.update(document_id="doc_id", data={"title": "Q2 Plan v2"})
await client.writer.documents.download(document_id="doc_id", output_format="pdf")
await client.writer.documents.delete(document_id="doc_id")
```
