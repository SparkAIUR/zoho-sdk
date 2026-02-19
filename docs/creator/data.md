# Creator Data API

## List Records

```python
records = await client.creator.data.list_records(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
    from_index=1,
    limit=200,
)
print(len(records.data))
```

## Add Records

```python
resp = await client.creator.data.add_records(
    account_owner_name="owner",
    app_link_name="inventory_app",
    form_link_name="orders",
    data={"Order_Name": "A-100", "Amount": 120},
)
print(resp.code)
```

## Update/Delete Record

```python
await client.creator.data.update_record(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
    record_id="123456700000001",
    data={"Amount": 140},
)

await client.creator.data.delete_record(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
    record_id="123456700000001",
)
```
