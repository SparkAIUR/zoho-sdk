# CRM Dynamic Discovery

`client.crm.dynamic` allows runtime module discovery and dynamic module-bound clients.

## Direct Attribute Access

```python
leads = client.crm.dynamic.Leads

result = await leads.list(page=1, per_page=200)
lead = await leads.get(record_id="123456789")
```

Each dynamic module client maps to `client.crm.records` methods with `module` pre-bound:

- `get(record_id=..., fields=...)`
- `list(page=..., per_page=..., fields=...)`
- `iter(per_page=..., fields=...)`
- `create(data=...)`
- `update(record_id=..., data=...)`
- `delete(record_id=...)`

## Discover Available Modules

```python
modules = await client.crm.dynamic.list_modules()
print(modules)

if await client.crm.dynamic.has_module("Leads"):
    leads = await client.crm.dynamic.get_module_client("Leads")
```

`get_module_client(...)` validates against metadata and raises `KeyError` for unknown modules.

## Precompile + Persistent Cache

Warm and persist module discovery metadata (for fast process restarts):

```python
await client.crm.dynamic.precompile_modules()
```

By default, dynamic discovery caches are stored under:

- Unix/Linux/macOS: `~/.cache/zohosdk/crm/...`
- Windows: `%LOCALAPPDATA%\\zohosdk\\crm\\...` (fallback to `%APPDATA%`)
