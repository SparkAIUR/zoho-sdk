# Sheet Workbooks API

## List Workbooks

```python
workbooks = await client.sheet.workbooks.list(limit=50)
print(workbooks.workbooks)
```

## Create/Delete Workbook

```python
created = await client.sheet.workbooks.create(data={"name": "Q1 Planning"})
await client.sheet.workbooks.delete(workbook_id="workbook_123")
```
