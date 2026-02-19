# Creator Meta API

## Get Sections

```python
sections = await client.creator.meta.get_sections(
    account_owner_name="owner",
    app_link_name="inventory_app",
)
print(sections.code, len(sections.data))
```

## Get Forms and Reports

```python
forms = await client.creator.meta.get_forms(
    account_owner_name="owner",
    app_link_name="inventory_app",
)
reports = await client.creator.meta.get_reports(
    account_owner_name="owner",
    app_link_name="inventory_app",
)
print(forms.message, reports.message)
```

## Get Form Fields

```python
fields = await client.creator.meta.get_form_fields(
    account_owner_name="owner",
    app_link_name="inventory_app",
    form_link_name="orders",
)
print(fields.first_data)
```
