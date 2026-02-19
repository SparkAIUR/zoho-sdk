# Getting Started

## Install

```bash
uv add zoho
```

## Recommended Initialization

Use explicit credentials for clarity and portability:

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    dc="US",
    environment="production",
)
```

## First API Call

```python
async with client:
    org = await client.crm.org.get()
    print(org)
```

## Local Development

```bash
uv sync --group dev
uv run pytest
uv run ruff check .
uv run mypy
```
