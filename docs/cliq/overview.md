# Cliq Overview

`client.cliq` provides typed access to Zoho Cliq v2 APIs.

## Common Use Cases

- list users/channels/chats for tenant graph discovery
- read and post messages for workflow automations
- inspect/manage thread followers

## Quick Example

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

channels = await client.cliq.channels.list(limit=50)
for row in channels.result_rows:
    print(row.get("name"), row.get("id"))
```

## Scope Notes

Typical read bundle:
- `ZohoCliq.Users.READ`
- `ZohoCliq.Chats.READ`
- `ZohoCliq.Channels.READ`
- `ZohoCliq.Messages.READ`
