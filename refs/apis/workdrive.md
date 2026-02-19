# Zoho WorkDrive API Research

Source:
- https://workdrive.zoho.com/apidocs/v1/overview

## Product Fit For Ingestion

Strong fit for enterprise search:
- File/folder metadata graph
- Search endpoints
- Recent changes (delta sync)
- Team and team-folder admin entities for tenancy/topology

## Authentication

- OAuth 2.0 with `Zoho-oauthtoken` bearer format.
- Scope naming pattern: `WorkDrive.<scope-name>.<operation>`.
- Example from docs: `WorkDrive.team.ALL` and granular `CREATE/READ/UPDATE/DELETE` operations.

## Base URL and Multi-DC

Docs provide DC-specific base API URIs. Core pattern:
- `https://www.zohoapis.<tld>/workdrive/`
- API paths frequently use `/api/v1/...`.

SDK requirements:
- Map DC -> base domain
- Keep `workdrive_base_url` explicit override
- Handle JSON API and download-host differences when binary download support is added

## Pagination

WorkDrive documents both:
- Offset pagination (`page[offset]`, `page[limit]`)
- Cursor pagination (`page[next]` with `links.cursor.next`)

Connector impact:
- Delta iterators should prioritize cursor mode when available.
- Checkpoint model must support `cursor` continuation token.

## Response and Data Shape

- JSON:API style envelopes (`data`, `attributes`, `relationships`, `links`, `meta`).
- Errors may be in structured `errors` arrays.

## MVP Endpoint Bundle

- Files: get/trash/restore/delete
- Folders: list children/create/rename
- Search: query
- Changes: list recent changes for delta sync
- Admin: list teams/team members/team folders

## Integration Risks

- Endpoint naming is resource-rich and can vary between admin and non-admin flows.
- Pagination mode differs by endpoint.
- Requires robust permission/scope alignment to avoid connector crawl failures.

## Notes For `pipeshub-ai` Ingestion

- Build primary crawlers from folders + recent changes.
- Normalize JSON:API resources to canonical ingestion documents.
- Persist checkpoints with `cursor` first, fallback to `offset`.
