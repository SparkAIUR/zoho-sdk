# Overview

## Problem statement

The existing Zoho CRM Python SDK is **sync-first** and is oriented around a large, Java-style class hierarchy. It works, but it imposes friction for:
- modern async Python apps (FastAPI, asyncio workers, etc.)
- performance (blocking I/O, limited batching/concurrency controls)
- maintainability (hard to track upstream API changes unless you adopt Zoho’s SDK structure)

This project designs a **modern, async-first unified Python SDK** that:
1. supports **Zoho CRM** first, and expands to other Zoho products (Creator, Analytics, Projects)
2. maintains **upstream compatibility** by generating code from canonical specs
3. has first-class developer experience: typing, IDE autocomplete, predictable errors, easy auth, and sensible defaults

## Goals

### Runtime & DX
- **Async-first**: every network call is `async` and uses connection pooling.
- **Optional sync wrapper**: provide a small sync facade for users who can’t use asyncio.
- **Type-safe** request/response models with good IDE autocomplete.
- **Predictable errors**: structured exception types with request id / response body.
- **Pagination helpers**: async iterators for list endpoints.
- **Config ergonomics**: env-var first, but supports explicit config objects.

### Spec-driven generation
- CRM models generated from Zoho’s SDK `json_details.json` (to stay aligned with upstream SDK semantics), and endpoints from Zoho CRM’s OAS when available.
- Creator + Analytics endpoints/models generated from their OAS downloads.
- Projects generated from an extracted spec (until an official OAS is available).
- A single generator pipeline that can be re-run in CI to update generated code.

### Token caching
- A pluggable, async token store with backends:
  - Redis (if provided/available)
  - SQLite (default persistent cache)
  - Memory (tests / ephemeral)
- Safe refresh behavior with per-token locking to prevent refresh storms.

## Non-goals

- Re-implementing every high-level “business workflow” abstraction Zoho may provide.
- Hiding Zoho’s API model entirely. We provide a clean SDK surface, but keep a close mapping to endpoints.
- Supporting legacy Python versions. Target: Python 3.10+ (recommend 3.11+).

## User-facing API sketch

```python
from zoho_sdk import Zoho

zoho = Zoho.from_env()  # reads env vars, configures token cache, transports

# CRM
lead = await zoho.crm.records.get(module="Leads", record_id="123")
await zoho.crm.records.update(module="Leads", record_id="123", data={"Last_Name": "Smith"})

# Projects
projects = [p async for p in zoho.projects.projects.list(portal_id="60028147039")]

# Analytics
workspaces = await zoho.analytics.workspaces.list(org_id="123456789")

# Creator
sections = await zoho.creator.meta.sections.get(account_owner="alice", app_link_name="my-app")
```

## Repository layout (proposed)

```
src/zoho_sdk/
  __init__.py
  _core/
    config.py
    transport.py
    auth/
      oauth2.py
      token_store.py
      stores/
        memory.py
        sqlite.py
        redis.py
    errors.py
    pagination.py
    models.py
    telemetry.py
  crm/
    __init__.py
    generated/...
    records.py
    metadata.py
  creator/
    generated/...
  analytics/
    generated/...
  projects/
    generated/...
tools/
  codegen/
    main.py
    ir.py
    loaders/
      crm_json_details.py
      openapi.py
      projects_extractor.py
    templates/
tests/
  golden/
  integration/
docs/
pyproject.toml
```

