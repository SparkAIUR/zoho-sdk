# Errors

The SDK exposes typed exceptions for better flow control and debugging.

## Common Exceptions

- `ZohoAuthError`
- `ZohoRateLimitError`
- `ZohoValidationError`
- `ZohoNotFoundError`
- `ZohoServerError`
- `ZohoTransportError`

## Example

```python
from zoho.core.errors import ZohoRateLimitError

try:
    await client.crm.records.list(module="Leads")
except ZohoRateLimitError as exc:
    print(exc.retry_after)
```

Each API error carries context such as status code, request id (if available), and short response payload details.
