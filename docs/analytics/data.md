# Analytics Data API

Create/update/delete rows on table views using `CONFIG` payloads.

```python
await client.analytics.data.create_rows(
    workspace_id="workspace_id",
    view_id="table_view_id",
    config={"rows": [{"Email": "alex@example.com"}]},
)

await client.analytics.data.update_rows(
    workspace_id="workspace_id",
    view_id="table_view_id",
    config={"criteria": '"Email"=\'alex@example.com\'', "rows": [{"Status": "Active"}]},
)
```
