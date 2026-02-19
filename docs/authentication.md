# Authentication

## OAuth Refresh Token Flow

The SDK currently targets server-side OAuth refresh token flow.

Required inputs:
- `client_id`
- `client_secret`
- `refresh_token`
- data center (`dc`)
- environment (`production`, `sandbox`, or `developer`)

## Token Stores

- `memory`: in-memory only (tests, short-lived scripts)
- `sqlite` (default): persistent local cache
- `redis`: distributed worker scenarios

Example:

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    token_store_backend="redis",
    redis_url="redis://localhost:6379/0",
)
```

## Domain Correctness

Token/domain data is keyed by data center and environment to prevent cross-environment token reuse.
