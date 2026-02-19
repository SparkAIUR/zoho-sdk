# CRM Modules

Module metadata calls are frequently reused and can be cached.

## List Modules

```python
modules = await client.crm.modules.list(use_cache=True, cache_ttl_seconds=3600)
```

## Get a Module

```python
lead_module = await client.crm.modules.get("Leads", use_cache=True)
```

## Caching Behavior

- Cache is in-memory per client process.
- `cache_ttl_seconds` lets callers override default TTL for targeted calls.
- Set `use_cache=False` for forced fresh reads.
