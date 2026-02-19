# Projects Overview

`zoho.projects` currently targets Zoho Projects API V3 endpoints.

## Initialize

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    projects_default_portal_id="12345678",  # optional
)
```

## Subclients

- `client.projects.portals`
- `client.projects.projects`
- `client.projects.tasks`

If you do not set `projects_default_portal_id`, pass `portal_id` explicitly per call.

List/get operations return typed models (`Portal`, `Project`, `Task`) with permissive extra fields.
