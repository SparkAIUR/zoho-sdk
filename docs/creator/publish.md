# Creator Publish API

Use publish APIs when interacting with published app/report/form endpoints.

## List and Add

```python
rows = await client.creator.publish.list_records(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
)
print(rows.code, len(rows.data))

await client.creator.publish.add_records(
    account_owner_name="owner",
    app_link_name="inventory_app",
    form_link_name="orders",
    data={"Order_Name": "P-101"},
)
```

## Update/Delete

```python
await client.creator.publish.update_record(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
    record_id="123456700000001",
    data={"Order_Name": "P-102"},
)

await client.creator.publish.delete_record(
    account_owner_name="owner",
    app_link_name="inventory_app",
    report_link_name="all_orders",
    record_id="123456700000001",
)
```
