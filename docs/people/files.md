# People Files API

## List Files

```python
files = await client.people.files.list(limit=100)
print(files.result_rows)
```

## Get/Delete File Metadata

```python
file_meta = await client.people.files.get(file_id="ab12cd34")
await client.people.files.delete(file_id="ab12cd34")
```
