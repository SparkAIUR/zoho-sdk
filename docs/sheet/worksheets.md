# Sheet Worksheets API

## List Worksheets

```python
worksheets = await client.sheet.worksheets.list(workbook_id="workbook_123")
print(worksheets.worksheets)
```

## Create/Rename/Delete Worksheet

```python
await client.sheet.worksheets.create(
    workbook_id="workbook_123",
    data={"name": "Data"},
)

await client.sheet.worksheets.rename(
    workbook_id="workbook_123",
    worksheet_id="worksheet_42",
    name="Data Archive",
)

await client.sheet.worksheets.delete(
    workbook_id="workbook_123",
    worksheet_id="worksheet_42",
)
```
