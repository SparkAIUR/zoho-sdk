# WorkDrive Recent Changes API

## List Recent Changes

```python
changes = await client.workdrive.changes.list_recent(
    folder_id="folder_123",
    limit=200,
)

cursor = None
if isinstance(changes.links.get("cursor"), dict):
    cursor = changes.links["cursor"].get("next")
print(cursor)
```
