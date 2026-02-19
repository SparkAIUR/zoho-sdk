# People Forms API

## List Forms

```python
forms = await client.people.forms.list_forms()
print(len(forms.result_rows))
```

## List/Search Records

```python
records = await client.people.forms.list_records(
    form_link_name="employee",
    from_index=0,
    limit=200,
)

matches = await client.people.forms.search_records(
    form_link_name="employee",
    criteria="Email='user@example.com'",
)
```

## Create/Update Record

```python
created = await client.people.forms.create_record(
    form_link_name="employee",
    data={"Name": "Alex"},
)

updated = await client.people.forms.update_record(
    form_link_name="employee",
    record_id="123456",
    data={"Name": "Alex Chen"},
)
```
