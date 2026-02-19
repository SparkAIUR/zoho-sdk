# Sheet Tabular API

## Fetch Records

```python
rows = await client.sheet.tabular.fetch_worksheet_records(
    workbook_id="workbook_123",
    worksheet_name="Data",
    offset=0,
    limit=500,
)
print(rows.records)
```

## Add/Update/Delete Records

```python
await client.sheet.tabular.add_worksheet_records(
    workbook_id="workbook_123",
    worksheet_name="Data",
    records=[{"Email": "user@example.com"}],
)

await client.sheet.tabular.update_worksheet_records(
    workbook_id="workbook_123",
    worksheet_name="Data",
    criteria="Email='user@example.com'",
    updates={"Status": "Active"},
)

await client.sheet.tabular.delete_worksheet_records(
    workbook_id="workbook_123",
    worksheet_name="Data",
    criteria="Status='Inactive'",
)
```
