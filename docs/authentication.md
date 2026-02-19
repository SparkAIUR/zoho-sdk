# Authentication

## Required Credentials

The SDK uses Zoho OAuth refresh-token flow and requires:

- `client_id`
- `client_secret`
- `refresh_token`
- `dc` (`US`, `EU`, `IN`, `AU`, `JP`, `CA`, `SA`, `CN`)
- `environment` (`production`, `sandbox`, `developer`)

## Credential Setup Guide

Use the dedicated step-by-step guide to obtain credentials correctly:

- [Credential Setup (Zoho OAuth)](auth-credentials.md)

That guide covers:
- creating a Zoho OAuth client in API Console
- choosing scopes for CRM operations
- generating and exchanging grant codes
- data center domain mapping
- SDK configuration examples

## SDK Initialization

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

## Token Stores

- `memory`: in-memory only (tests, short-lived scripts)
- `sqlite` (default): persistent local cache
- `redis`: distributed worker scenarios

```python
client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    token_store_backend="redis",
    redis_url="redis://localhost:6379/0",
)
```

## Domain and Environment Correctness

Token/domain cache keys include data center + environment to prevent cross-region or cross-environment token reuse bugs.
