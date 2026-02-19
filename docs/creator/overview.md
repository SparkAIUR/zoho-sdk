# Creator Overview

`zoho.creator` provides async access to Zoho Creator APIs across:

- metadata (`meta`)
- data APIs (`data`)
- publish APIs (`publish`)
- dynamic application discovery (`dynamic`)

## Initialize

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    creator_environment_header="development",  # optional: development/stage/production
)
```

## Subclients

- `client.creator.meta`
- `client.creator.data`
- `client.creator.publish`
- `client.creator.dynamic`

See [Creator Dynamic Discovery](discovery.md) for runtime app discovery and precompiled cache usage.

Most Creator methods return a typed `CreatorResponse` envelope:

- `response.code`
- `response.message`
- `response.data` (list of permissive `CreatorRecord` models)
