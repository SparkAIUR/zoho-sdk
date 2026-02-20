# Writer Merge API

```python
fields = await client.writer.merge.get_fields(document_id="template_doc_id")
```

Merge workflows:

```python
await client.writer.merge.merge_and_download(
    document_id="template_doc_id",
    data={"customer_name": "Acme Corp"},
    output_format="pdf",
)

await client.writer.merge.merge_and_send(
    document_id="template_doc_id",
    data={"customer_name": "Acme Corp"},
    email_to=["ops@example.com"],
)
```
