# CRM COQL

Use COQL when you need cross-module fields, richer filters, or explicit query control.

Required OAuth scope:

- `ZohoCRM.coql.READ`

## Raw Query Text

```python
--8<-- "examples/crm/coql.py:raw_query"
```

## Fluent Builder

```python
--8<-- "examples/crm/coql.py:builder_query"
```

## Multi-Page Fetch

`execute()` runs a single query call. Use `execute_all()` for offset-based paging.

```python
--8<-- "examples/crm/coql.py:execute_all"
```

## Notes

- Use named parameters (`:name`) for safer value interpolation.
- `execute_all()` rejects queries that already include `LIMIT`.
- Builder queries are immutable: each chained call returns a new builder instance.
