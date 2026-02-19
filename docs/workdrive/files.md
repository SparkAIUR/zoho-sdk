# WorkDrive Files API

## Get File Metadata

```python
file_meta = await client.workdrive.files.get(file_id="f_xxx")
print(file_meta.resources)
```

## Trash / Restore / Delete

```python
await client.workdrive.files.trash(file_id="f_xxx")
await client.workdrive.files.restore(file_id="f_xxx")
await client.workdrive.files.delete(file_id="f_xxx")
```
