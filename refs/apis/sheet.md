# Zoho Sheet API Research

Source:
- https://sheet.zoho.com/help/api/v2/

## Product Fit For Ingestion

High-value sources for enterprise search:
- Workbook metadata
- Worksheet/tabular row data
- Structured table records (suitable for indexing)

## Authentication

- OAuth 2.0 required.
- Token sent via `Authorization: Zoho-oauthtoken <token>`.
- Access token short-lived; refresh token flow required for long-running connectors.

## Base URL and Versions

- Documentation is under API v2.
- SDK should default to `.../api/v2` path semantics and keep explicit base URL override (`sheet_base_url`).

## Rate Limits and Lock Behavior

Docs state:
- No daily/monthly hard cap currently documented.
- Per-minute API limits exist per document.
- If exceeded, APIs on that document can lock for around 5 minutes.

Implication for SDK:
- Add conservative default page size and paced fetch loops.
- Backoff and jitter should be enabled for connector flows.

## Response and Data Shape

- Endpoints return varying envelopes across workbook/worksheet/tabular operations.
- For ingestion, normalize row payloads from `records`/`data` arrays.

## MVP Endpoint Bundle

- Workbooks: list/get/create/delete
- Worksheets: list/create/rename/delete
- Tabular records: fetch/add/update/delete worksheet records

## Integration Risks

- Docs are broad and endpoint path specifics vary by operation.
- Pagination and criteria filters are endpoint-specific.
- Keep request models permissive and support passthrough params.

## Notes For `pipeshub-ai` Ingestion

- Use worksheet-level row extraction as first-class iterator.
- Track checkpoints by numeric offset.
- Emit stable document IDs from row identifiers when available.
