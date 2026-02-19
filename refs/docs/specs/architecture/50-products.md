# Products

This document captures product-specific requirements that influence the unified SDK design.

---

## Zoho CRM

### API version
- V8

### Notable SDK behaviors to replicate
- Token persistence options exist in the official SDK.
- Field metadata can be cached locally to validate record operations before sending (saves API credits).

### Spec sources
- CRM OAS v8 repository
- `json_details.json` from Zoho CRM Python SDK

### Dynamic schemas (Records)
CRM record fields differ per org and per module.
Approach:
- Provide a `Record` type that behaves like a mapping, but can be “typed” using fetched module schema.
- Cache module schema in cache backend (SQLite/Redis) with TTL (e.g., 24h) and ETag support if available.

---

## Zoho Creator

### API version
- v2.1 recommended

### Base URL
- Depends on region/data center; Creator docs show `base_url` like `www.zohoapis.com` (US) vs `www.zohoapis.eu` (EU).

### Spec sources
- OAS downloads from Creator docs (some endpoints offer downloadable OAS per endpoint)
- Consider building an OAS aggregator tool to produce a single unified spec.

### Special headers
- Some endpoints use `environment: development` / stage header.

---

## Zoho Analytics

### API version
- v2 data API

### Base URL & org-id
- Analytics requires region-specific `analyticsapi.zoho.*` hosts and requires the `ZANALYTICS-ORGID` header.

### Spec sources
- Zoho Analytics OAS + docs

### Quirks
- Some operations require passing JSON in a query-string `CONFIG` parameter.
- Some error codes may appear in response bodies even when HTTP status is 200 (SDK should be defensive).

---

## Zoho Projects

### API version
- V3 (migration deadline enforced by Zoho; older APIs deprecated)

### Base URL
- Region-specific: `projectsapi.zoho.<tld>` with `/api/v3/...`
- URLs are portal-scoped: `/portal/{portal_id}/...`

### Spec sources
- No official OAS found in this design; use a docs extractor to create an internal OpenAPI-like spec.

### Quirks
- Many endpoints require portal_id, and pagination patterns vary by endpoint.

