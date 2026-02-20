# Zoho Analytics API Research

Source:
- https://www.zoho.com/analytics/api/v2/introduction.html
- https://www.zoho.com/analytics/api/v2/prerequisites.html
- https://www.zoho.com/analytics/api/v2/api-specification.html
- https://www.zoho.com/analytics/api/v2/open-api-specification.html
- https://github.com/zoho/analytics-oas/tree/main/v2.0

## Product Fit For Ingestion

Strong fit for enterprise reporting/search ingestion:
- Workspace/view metadata graph
- Row-level table extraction (data API and bulk export APIs)
- Scheduled/import/export job state for incremental pipelines

## Authentication

- OAuth 2.0 with Zoho Accounts domain matching the Analytics DC.
- Header format: `Authorization: Zoho-oauthtoken <token>`.
- Many endpoints also require `ZANALYTICS-ORGID: <org_id>` header.
- Scope families:
  - `ZohoAnalytics.metadata.*`
  - `ZohoAnalytics.data.*`
  - `ZohoAnalytics.bulk.*` (represented in OAS as `data` scope for import/export)
  - `ZohoAnalytics.modeling.*`, `share.*`, `embed.*`, `usermanagement.*`

## Base URL and Multi-DC

Base API pattern: `https://analyticsapi.zoho.<tld>/restapi/v2/...`.

SDK requirements:
- DC-aware defaults
- Explicit `analytics_base_url` override
- Ensure CONFIG query encoding remains deterministic for signed/cacheable requests

## Pagination and Limits

- API uses endpoint-specific patterns (`CONFIG` query payload, job polling, export handles).
- Metadata/data endpoints are generally request-volume sensitive; no single global limit table surfaced in the docs pages we relied on.

Connector implication:
- default to batch-oriented extraction via bulk export APIs when available
- support resumable job polling checkpoints

## MVP Endpoint Bundle

- Metadata: orgs/workspaces/views/dashboards/metadetails
- Data: create/update/delete rows on table views
- Bulk: import/export + import/export job status + export download endpoint

## Notes For `pipeshub-ai` Ingestion

- Primary ingestion should normalize workspace/view metadata + exported row payloads.
- Persist checkpoints by job IDs and export windows.
- Include org/workspace/view IDs in metadata for tenant-safe indexing.
