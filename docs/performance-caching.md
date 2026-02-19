# Performance & Caching

## Runtime Performance Defaults

- Connection pooling via `httpx.AsyncClient`
- Retry on transient failures and rate limits
- Lazy-loading for product operation clients

## Caching Strategies

### Token Caching

- SQLite-backed token storage is the default for reliable local persistence.
- Redis token storage is available for distributed workers.

### Metadata Caching

- CRM metadata endpoints can be cached in-memory per client instance.
- Toggle globally via settings or per call with `use_cache` and `cache_ttl_seconds`.

## Logging for Ops

Use JSON logs in containerized environments:

```python
Zoho.from_credentials(..., log_format="json")
```
