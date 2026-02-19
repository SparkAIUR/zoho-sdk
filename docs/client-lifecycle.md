# Client Lifecycle

The SDK supports both lifecycle patterns:

- context manager (`async with client`)
- long-lived client without context manager

## When To Use `async with`

Use a context manager for one-shot tasks:

- scripts
- cron jobs
- CLI commands
- short background jobs

```python
from zoho import Zoho

async with Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
) as client:
    org = await client.crm.org.get()
    print(org)
```

This guarantees transport/auth resources are closed automatically.

## When To Use A Long-Lived Singleton

Use a singleton for web apps and workers where you want pooled connections across requests/jobs.

```python
from zoho import Zoho

zoho_client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

# reuse `zoho_client` across handlers/jobs
lead = await zoho_client.crm.records.get(module="Leads", record_id="123456789")
```

Call `await zoho_client.close()` once during shutdown.

## FastAPI Example

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from zoho import Zoho

zoho_client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await zoho_client.close()

app = FastAPI(lifespan=lifespan)
```

## Lifecycle Rules

- Do not create a new client per request.
- Reuse a single client per process/event loop when possible.
- After `close()`, the client is terminal (`client.closed` is `True`) and should be replaced with a new instance.
