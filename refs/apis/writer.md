# Zoho Writer API Research

Source:
- https://www.zoho.com/writer/help/api/v1/getting-started.html
- https://www.zoho.com/writer/help/api/v1/oauth-2.html
- https://www.zoho.com/writer/help/api/v1/writer-apis-threshold-limits.html

## Product Fit For Ingestion

High-value document ingestion surface:
- document and folder metadata
- merge-ready template data
- export/download workflows for indexable content

## Authentication

- OAuth 2.0 with standard Zoho authorization-code/refresh-token flow.
- Primary scopes documented:
  - `ZohoWriter.documentEditor.ALL`
  - `ZohoWriter.merge.ALL`
- Some workflows may require additional scopes from adjacent products:
  - `ZohoPC.files.ALL`, `WorkDrive.files.ALL`, `WorkDrive.organization.ALL`, `WorkDrive.workspace.ALL`, `ZohoSign.documents.ALL`

## Base URL and Multi-DC

Writer docs specify endpoint:
- `https://www.zohoapis.com/writer/api/v1`

DC-specific TLD variants apply.

SDK requirements:
- DC-aware defaults
- Explicit `writer_base_url` override
- Keep API and account domains in same DC for token workflows

## Limits and Lock Behavior

Writer publishes per-API threshold and cooling windows.
Examples from threshold doc:
- document APIs often around 100 req/min with cooldown windows
- merge APIs around 100 req/min with minute/hour/day cooling limits

Connector implication:
- page reads and export operations should be throttled predictably
- retry/backoff should respect longer cooling periods for merge/export heavy flows

## MVP Endpoint Bundle

- Documents: list/get/create/update/delete/restore/download
- Folders: list/get/create/update/delete
- Merge: get fields, merge-and-download/store/send

## Notes For `pipeshub-ai` Ingestion

- Prioritize read-only document/folder crawls for content indexing.
- Use document IDs + modified timestamps for incremental sync.
- Store source metadata (folder, owner, update time) for ranking/filtering.
