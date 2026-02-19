# CRM Records

## Get a Record

```python
lead = await client.crm.records.get(
    module="Leads",
    record_id="123456789",
    fields=["Last_Name", "Email"],
)
```

## List Records

```python
resp = await client.crm.records.list(module="Leads", page=1, per_page=200)
print(resp.info)
print(resp.data)
```

## Iterate Records

```python
async for record in client.crm.records.iter(module="Leads", per_page=200):
    print(record.id)
```

## Create / Update / Delete

```python
await client.crm.records.create(module="Leads", data={"Last_Name": "Ng"})
await client.crm.records.update(module="Leads", record_id="123456789", data={"Last_Name": "Chen"})
await client.crm.records.delete(module="Leads", record_id="123456789")
```
