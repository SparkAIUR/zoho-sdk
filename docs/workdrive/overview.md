# WorkDrive Overview

`zoho.workdrive` provides file graph, search, recent changes, and admin APIs.

## Initialize

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    workdrive_base_url="https://www.zohoapis.com",  # optional override
)
```

## Subclients

- `client.workdrive.files`
- `client.workdrive.folders`
- `client.workdrive.search`
- `client.workdrive.changes`
- `client.workdrive.admin`

WorkDrive responses are exposed as `WorkDriveResponse` with JSON:API-aware resource parsing.
