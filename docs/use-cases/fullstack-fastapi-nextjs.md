# Full Stack Application (FastAPI + Next.js)

This pattern is for SaaS applications that connect tenant/user Zoho accounts through OAuth and keep grant handling server-side.

## Backend (FastAPI)

### OAuth Settings

```python
--8<-- "examples/fullstack_fastapi_nextjs/backend.py:oauth_settings"
```

### Start OAuth (tenant-scoped)

```python
--8<-- "examples/fullstack_fastapi_nextjs/backend.py:oauth_start"
```

### Callback + Token Exchange

```python
--8<-- "examples/fullstack_fastapi_nextjs/backend.py:oauth_callback"
```

### Non-Sensitive Token Status Endpoint

```python
--8<-- "examples/fullstack_fastapi_nextjs/backend.py:tenant_token_lookup"
```

## Frontend (Next.js App Router, TypeScript)

### Connect Route

```ts
--8<-- "examples/fullstack_fastapi_nextjs/nextjs/app/api/zoho/connect/route.ts:connect_route"
```

### Callback Route

```ts
--8<-- "examples/fullstack_fastapi_nextjs/nextjs/app/api/zoho/callback/route.ts:callback_route"
```

### Integrations Page

```tsx
--8<-- "examples/fullstack_fastapi_nextjs/nextjs/app/integrations/zoho/page.tsx:connect_ui"
```

## Notes

- Keep client secret and refresh token handling in the backend only.
- Persist tenant tokens in an encrypted store (database or KMS-backed secret manager).
- Validate OAuth `state` for every callback to prevent CSRF and tenant mix-ups.
