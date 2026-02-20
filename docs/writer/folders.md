# Writer Folders API

```python
folders = await client.writer.folders.list(limit=100)
folder = await client.writer.folders.create(name="Legal")
await client.writer.folders.update(folder_id="folder_id", data={"name": "Legal Archive"})
```
