# Zoho API Integration Matrix (People, Sheet, WorkDrive)

## Scope Summary

| Product | Primary API Version | High-Value Ingestion Surface | Pagination Model | Special Notes |
|---|---|---|---|---|
| People | mixed docs (V1/V2/V3 sections) | forms, employees, files | mostly offset/list APIs | endpoint threshold lock windows |
| Sheet | v2 | workbook/worksheet/tabular rows | offset/list style | per-document rate lock behavior |
| WorkDrive | v1 | files/folders/search/recent changes/admin graph | offset + cursor | JSON:API envelope + multi-DC base URIs |

## Cross-Product Requirements For SDK

- OAuth refresh-token flow with explicit connection profiles.
- Multi-account routing to isolate tenant tokens and settings.
- Product-specific base URL overrides (`people_base_url`, `sheet_base_url`, `workdrive_base_url`).
- Connector-oriented iterators with checkpoint support (`offset` and `cursor`).
- Conservative retry/backoff behavior to handle lock windows and threshold limits.

## Initial Delivery Contract

- Raw product clients for balanced CRUD in selected MVP bundles.
- SDK-native ingestion iterators for connector pipelines (`zoho.ingestion`).
- Env-gated integration smoke tests for all new products.
- Documentation with both raw API and ingestion workflow examples.
