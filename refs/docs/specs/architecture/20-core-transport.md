# Core transport

## Transport contract

The transport layer should:
- send HTTP requests (async)
- support request/response hooks
- apply retries and backoff
- apply rate-limit handling (429, Retry-After, product-specific patterns)
- provide structured errors

Proposed interface:

```python
class Transport(Protocol):
    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
        idempotency_key: str | None = None,
    ) -> Response:
        ...
```

## Implementation

### HTTP client
- `httpx.AsyncClient` with connection pooling
- default `limits` tuned for concurrency, but configurable

### Serialization
- JSON: use stdlib `json` by default, optional `orjson` accelerator.

### Error handling
Raise typed exceptions:
- `ZohoAPIError` (base)
- `ZohoAuthError` (401/invalid token)
- `ZohoRateLimitError` (429 or product-specific)
- `ZohoNotFoundError` (404)
- `ZohoValidationError` (400)
- `ZohoServerError` (>=500)
Each error should include:
- status code
- parsed error payload (if any)
- request id header when available
- method + url (scrubbed)
- response text (truncated)

## Retry policy

### Safe retry conditions
- Transport errors where request likely did not reach server (connection reset, DNS, TLS handshake, timeout before send)
- 5xx responses (except those known to be non-transient)
- 429 with Retry-After
- Product-specific: Analytics may return rate limit error codes in JSON while HTTP status is 200.

### Unsafe retry conditions (default no retry)
- 4xx other than 429
- 409 conflicts unless endpoint docs state safe
- POST/PUT without idempotency semantics (unless caller opts in)

### Backoff
- exponential with jitter: `base * 2**attempt`, capped
- for 429 respect `Retry-After` when present

## Pagination

Expose helpers:
- `AsyncPager` for “page/limit” style
- `AsyncCursorPager` for “next_page_token” style

API shape:

```python
async for item in zoho.crm.records.iter(module="Leads", page_size=200):
    ...
```

## Sync wrapper

Provide `ZohoSync` which wraps `AsyncTransport` via `anyio.from_thread.run` or a separate `httpx.Client` implementation.
Keep it thin and avoid duplicating behavior.

