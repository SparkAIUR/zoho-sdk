# WorkDrive Folders API

## List Folder Children

```python
children = await client.workdrive.folders.list_children(
    folder_id="folder_123",
    limit=200,
)
print(children.resources)
```

## Create/Rename Folder

```python
await client.workdrive.folders.create(parent_id="folder_123", name="New Folder")
await client.workdrive.folders.rename(folder_id="folder_456", name="Renamed Folder")
```
