# Auth and token cache

## OAuth2 flows to support

At minimum:
- **Refresh token flow** (server-side apps): use `refresh_token + client_id + client_secret`
Optional (later):
- Authorization code exchange (for interactive apps)
- Device code flow (if Zoho supports it widely)

## Auth provider contract

```python
class AuthProvider(Protocol):
    async def get_headers(self) -> dict[str, str]:
        ...
```

The provider:
- returns `{"Authorization": "Zoho-oauthtoken <access_token>"}`
- refreshes when expired
- uses TokenStore for persistence

## Token data model

Key fields:
- `access_token: str`
- `expires_at: datetime`
- `refresh_token: str | None`
- `api_domain: str | None` (important for CRM; some Zoho token responses include it)
- `scopes: tuple[str, ...]`
- `dc: str` (US/EU/IN/AU/CN/JP/CA/SA, etc.)
- `environment: str` (prod/sandbox/dev where applicable)
- `created_at/updated_at`

Token key fields:
- `client_id`
- `user_id` (or org/user signature; some products are per-user)
- `dc + environment`
- product namespace (crm/creator/analytics/projects)

## Token store (Redis / SQLite)

### Requirements
- async APIs
- durable storage (SQLite default)
- atomic “refresh lock” per token key to prevent refresh storms
- TTL support (expire access tokens naturally)
- safe serialization (no leaking secrets in logs)

### Backend selection
- If `ZOHO_SDK_REDIS_URL` is configured AND redis dependency is installed: use Redis.
- Otherwise: use SQLite at `~/.cache/zoho_sdk/cache.sqlite3` (configurable).

### Redis backend
- Use Redis key: `zoho:token:{hash(token_key)}`
- Store JSON value with expiry as Redis TTL.
- Lock: `SET zoho:lock:{hash(token_key)} <uuid> NX PX <ttl_ms>`
- Release lock with Lua compare-and-del.

### SQLite backend
- Table `tokens`:
  - `key TEXT PRIMARY KEY`
  - `value BLOB`
  - `expires_at INTEGER` (unix)
  - `updated_at INTEGER`
- Table `locks`:
  - `key TEXT PRIMARY KEY`
  - `owner TEXT`
  - `expires_at INTEGER`
- Lock acquisition uses a transaction: insert if missing or expired; otherwise wait/backoff.

### Security notes
- Provide optional encryption-at-rest hook (BYOK) for SQLite values.
- Ensure secrets are redacted in repr/logging.

## Multi-process behavior

Goal: multiple workers can share a token store.

Algorithm:
1. Read token from store; if valid => use.
2. If expired, attempt acquire lock.
3. Winner refreshes token and writes it back.
4. Others wait and re-read.

## Domain & environment correctness

Zoho tokens are domain- and environment-specific. Token key MUST include:
- data center
- environment (prod/sandbox/dev when relevant)

This prevents subtle “works locally, fails in prod” bugs.

