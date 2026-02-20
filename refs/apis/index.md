# Zoho API Integration Matrix

## Scope Summary

| Product | Primary API Version | High-Value Ingestion Surface | Pagination Model | Special Notes |
|---|---|---|---|---|
| CRM | v8 | modules + records + org metadata | page/per_page | dynamic module discovery + cache |
| Creator | v2.1 | apps/forms/reports records | offset + cursor | dynamic app discovery + cache |
| Projects | v3 | portals/projects/tasks | offset/list style | portal-scoped topology |
| People | mixed docs (V1/V2/V3 sections) | forms, employees, files | mostly offset/list APIs | endpoint threshold lock windows |
| Sheet | v2 | workbook/worksheet/tabular rows | offset/list style | per-document rate lock behavior |
| WorkDrive | v1 | files/folders/search/recent changes/admin graph | offset + cursor | JSON:API envelope + multi-DC base URIs |
| Cliq | v2 | channels/chats/messages/threads/users | limit + next_token + time windows | per-endpoint threshold + lock periods |
| Analytics | v2 | org/workspace/view metadata + row/bulk export | CONFIG-based query + async job polling | `ZANALYTICS-ORGID` often required |
| Writer | v1 | documents/folders/merge artifacts | page/limit style + operation-specific constraints | explicit threshold/cooling tables |
| Mail | REST API index | accounts/folders/messages/threads | start + limit | broad module surface; scope granularity is endpoint-specific |

## Cross-Product Requirements For SDK

- OAuth refresh-token flow with explicit connection profiles.
- Multi-account routing to isolate tenant tokens and settings.
- Product-specific base URL overrides (`*_base_url`).
- Connector-oriented iterators with checkpoint support (`offset`, `cursor`, `page`).
- Conservative retry/backoff behavior to handle lock windows and threshold limits.

## Initial Delivery Contract

- Raw product clients for balanced CRUD in selected MVP bundles.
- SDK-native ingestion iterators for connector pipelines (`zoho.ingestion`).
- Env-gated integration smoke tests for all supported products.
- Documentation with both raw API and ingestion workflow examples.
