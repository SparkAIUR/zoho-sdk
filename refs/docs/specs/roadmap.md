# Roadmap

## Phase 0 — Project bootstrap (1–2 weeks)
- Repo scaffolding, CI, linting, formatting
- Core transport with httpx + basic retries
- Token store interface + SQLite implementation
- Minimal CRM “smoke” endpoints (e.g., Users, Org, Modules list)
- Integration test harness (env-driven secrets)

## Phase 1 — CRM foundations (2–6 weeks)
- CRM OAS ingestion + endpoint generator
- json_details ingestion + model generator
- CRM auth (api_domain handling)
- CRM metadata cache (module fields) with SQLite
- Record CRUD with dynamic field validation (opt-in strict mode)

## Phase 2 — Expand products (Creator + Analytics) (4–8 weeks)
- OAS ingestion for Creator + Analytics
- Product-specific headers + config
- Pagination helpers per product
- Shared error mapping improvements

## Phase 3 — Projects V3 (4–10 weeks)
- Build spec extractor (or curated spec)
- Implement key resources: portals, projects, tasks, users, timesheets
- Add regional endpoint mapping

## Phase 4 — Hardening
- Rate limiting + backpressure
- Structured tracing hooks
- Better streaming/file upload support
- Benchmarks + profiling

## Phase 5 — Compatibility & migration aids
- Migration guide from Zoho’s official CRM SDK
- Optional “compat layer” for common classes/names
- Deprecation policy and long-term maintenance

