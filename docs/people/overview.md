# People Overview

`zoho.people` provides access to People forms, employee directory, and files APIs.

## Initialize

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    people_base_url="https://people.zoho.com",  # optional override
)
```

## Subclients

- `client.people.forms`
- `client.people.employees`
- `client.people.files`

Responses are returned as `PeopleResponse` with permissive payload support.
