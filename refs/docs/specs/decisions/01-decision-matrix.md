# Decision matrix

This document records key architectural decisions in a way that can be revisited later.

## Scoring rubric

Each option is evaluated on:
- **DX** (typing, ergonomics, maintainability)
- **Performance** (CPU + I/O efficiency)
- **Reliability** (retries, rate-limits, correctness)
- **Spec-compatibility** (ability to stay aligned with upstream)
- **Complexity** (implementation + ongoing cost)

Scores: 1 (poor) to 5 (excellent)

---

## D1: Async HTTP stack

| Option | DX | Perf | Reliability | Complexity | Decision |
|---|---:|---:|---:|---:|---|
| httpx (AsyncClient) | 5 | 4 | 4 | 3 | ✅ Choose |
| aiohttp | 4 | 5 | 4 | 4 | |
| requests | 2 | 2 | 3 | 2 | |

**Rationale**
- `httpx` supports both async + sync under one API and has broad adoption.

---

## D2: Model layer

| Option | DX | Perf | Reliability | Complexity | Decision |
|---|---:|---:|---:|---:|---|
| Pydantic v2 models | 5 | 3 | 5 | 3 | ✅ Choose (default) |
| dataclasses + manual validation | 3 | 4 | 3 | 4 | |
| msgspec | 4 | 5 | 4 | 4 | optional future |

**Rationale**
- Pydantic provides outstanding IDE + runtime validation.
- We’ll keep a “thin model boundary” so switching is feasible later.

---

## D3: Spec sources

| Product | Primary spec | Secondary spec | Decision |
|---|---|---|---|
| CRM | Zoho CRM OAS v8 | `json_details.json` from Zoho CRM Python SDK | ✅ Use both (merge) |
| Creator | OAS downloads (per endpoint or aggregated) | Docs scraping fallback | ✅ OAS |
| Analytics | OAS repo + Zoho docs | Docs scraping fallback | ✅ OAS |
| Projects | Docs/spec extraction | community SDKs as reference only | ✅ Extracted spec |

**Rationale**
- OAS is best for endpoints.
- CRM `json_details.json` adds additional model metadata and helps keep parity with upstream SDK behavior.

---

## D4: Token persistence & caching

| Option | DX | Perf | Reliability | Complexity | Decision |
|---|---:|---:|---:|---:|---|
| Redis (async) | 4 | 5 | 5 | 4 | ✅ Supported |
| SQLite (async) | 5 | 4 | 4 | 3 | ✅ Default |
| Flat file JSON | 3 | 3 | 2 | 2 | fallback only |

**Rationale**
- SQLite provides “works everywhere” persistence without extra infra.
- Redis supports multi-process + multi-host deployments and distributed locks.

---

## D5: Retry strategy

| Option | DX | Perf | Reliability | Complexity | Decision |
|---|---:|---:|---:|---:|---|
| Custom policy + backoff + Retry-After | 5 | 4 | 5 | 4 | ✅ Choose |
| tenacity-only | 4 | 4 | 4 | 3 | |
| no retries | 1 | 5 | 1 | 1 | |

**Rationale**
- We need fine-grained rules: retry on transport errors, selective status codes, and product-specific behaviors (e.g., Analytics error codes).

---

## D6: Code generation

| Option | DX | Perf | Reliability | Complexity | Decision |
|---|---:|---:|---:|---:|---|
| IR + Jinja2 templates + ruff format | 5 | 4 | 5 | 4 | ✅ Choose |
| OpenAPI generator (external) | 3 | 4 | 4 | 2 | |
| Hand-written SDK | 2 | 4 | 3 | 5 | |

**Rationale**
- We need customization, cross-product consistency, and long-term maintainability.

