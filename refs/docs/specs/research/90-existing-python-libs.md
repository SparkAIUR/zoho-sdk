# Research: Existing Python libraries

This document reviews three Python packages and extracts what is useful for the unified SDK.

## zoho-projects-sdk

**What it is**
- A modern, async-first Projects SDK with strong typing and a clear internal architecture.

**Patterns worth adopting**
- Async-by-default surface
- Clear separation: ApiClient (transport) vs resource services vs models
- Strong typing via Pydantic models
- Explicit “configuration object” + env-driven configuration (good onboarding)

**Gaps / risks**
- Token persistence is not a first-class concept (in-memory only).
- Data center / regional accounts domains must be configurable; hardcoding is risky.
- Rate limiting (429) behavior must be first-class.

**Value to our implementation**
- Use as architectural inspiration (service modules + ApiClient pattern).
- Do *not* depend on it directly; implement a consistent core shared with other products.

## zoho-creator-sdk

**What it is**
- A modern, sync SDK with Pydantic models, httpx-based client, and a fluent interface.

**Patterns worth adopting**
- “Zero-config” env var initialization.
- Rich, structured error classes.
- Built-in rate limiting support (handles 429 and Retry-After).
- Criteria builder abstraction and pagination helpers.

**Gaps / risks**
- Sync-only (we want async-first).
- Repo availability may vary; design should not depend on this package.

**Value to our implementation**
- Adopt the DX patterns (criteria builder, pagination, strong exceptions).
- Re-implement in async style and share a unified token store.

## zoho-analytics-connector

**What it is**
- A practical, production-oriented Analytics client.
- Mixes v1 and v2 endpoints and includes higher-level helpers for import/export.

**Patterns worth adopting**
- Explicit configuration for accounts server URL + analytics server URL (region correctness).
- Token persistence concept (file-based persistence + override hooks).
- Defensive handling of rate limiting, including “rate limit error codes in-body”.

**Gaps / risks**
- Requests-based (sync) and older API style.
- API mix (v1/v2) may be confusing; unified SDK should clearly namespace.

**Value to our implementation**
- Use as a source of real-world edge cases: rate limit handling, error codes, region base URLs, and long-running import behavior.
- Re-implement using our core transport and caching.

