# Architecture

## High-level structure

The SDK is split into:
1. **Core runtime** (shared by all products)
2. **Product modules** (CRM, Creator, Analytics, Projects)
3. **Generated code** (models + endpoints) produced by the codegen pipeline

## Core runtime responsibilities

- Configuration loading
- OAuth2 token refresh
- Token storage + caching
- HTTP transport (async + optional sync)
- Retry & rate limit handling
- Serialization / deserialization
- Pagination and streaming helpers
- Observability hooks (logging, tracing)

## Product module responsibilities

Each product module:
- provides a product-scoped configuration (base URL, headers)
- exposes product-specific subclients and helper methods
- hosts generated endpoints and models
- contains “handwritten glue” where the API is dynamic or spec-incomplete

Examples:
- CRM has dynamic module fields and needs schema caching from metadata endpoints.
- Analytics requires org-id header and may return error codes in-body.
- Projects uses portal-scoped URLs and (today) lacks official OAS.
- Creator has environment header support and per-account base_url.

## Public API layout

```python
zoho = Zoho(...)
zoho.crm
zoho.creator
zoho.analytics
zoho.projects
```

Each subclient is a thin wrapper around:
- a shared `Transport`
- a shared `AuthProvider`
- product-specific `BaseUrlResolver` and default headers

## Dependency inversion points

To keep the SDK testable and extendable, these are all interfaces/protocols:
- `Transport` (http client)
- `AuthProvider` (adds auth header, handles refresh)
- `TokenStore` (Redis/SQLite/Memory)
- `CacheBackend` (optional shared cache for metadata)
- `Clock` (testable time)
- `Logger` (standard `logging` integration)

## Versioning strategy

- Semantic versioning for the Python package.
- Generated endpoints/models include an `upstream_spec_version` marker (commit hash or spec version string).
- Product submodules can optionally have their own version constants for API versions:
  - CRM: v8
  - Projects: v3
  - Analytics: v2
  - Creator: v2.1

