# Creator Dynamic Discovery

`client.creator.dynamic` provides runtime discovery of Creator applications and binds clients to discovered app/workspace pairs.

## List Applications

```python
applications = await client.creator.dynamic.list_applications()
for app in applications:
    print(app.get("workspace_name"), app.get("link_name"))
```

Discover only one workspace:

```python
owner_apps = await client.creator.dynamic.list_applications(account_owner_name="owner")
```

## Resolve Application Clients

```python
inventory = await client.creator.dynamic.get_application_client("owner.inventory-app")
forms = await inventory.meta.get_forms()
rows = await inventory.data.list_records(report_link_name="all_orders")
```

If app link names are unique, alias lookup works too:

```python
inventory = await client.creator.dynamic.get_application_client("inventory_app")
```

## Precompile + Persistent Cache

```python
await client.creator.dynamic.precompile_applications()
```

This writes discovery data to local disk cache for fast startup reloads.

Default cache locations:

- Unix/Linux/macOS: `~/.cache/zohosdk/creator/...`
- Windows: `%LOCALAPPDATA%\\zohosdk\\creator\\...` (fallback to `%APPDATA%`)

## Notes

- App names may collide across workspaces. Prefer `owner.app_link_name` for deterministic lookup.
- `get_application_client(...)` raises `KeyError` for unknown names.
