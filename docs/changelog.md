# Changelog

## Unreleased

- Added first-class CRM COQL support via `client.crm.coql`:
  - Raw COQL execution with named parameter binding (`execute(query=..., params=...)`)
  - Immutable fluent query builder (`select(...).from_(...).where(...).order_by(...).limit(...)`)
  - Explicit multi-page retrieval (`execute_all(...)`)
- Added typed COQL response models:
  - `CoqlInfo`
  - `CoqlQueryResponse`
- Added docs and snippet-backed examples for CRM COQL:
  - `docs/crm/coql.md`
  - `examples/crm/coql.py`

## v0.1.3

- Added Cliq ingestion iterators:
  - `iter_cliq_channel_documents(...)`
  - `iter_cliq_chat_documents(...)`
  - `iter_cliq_thread_documents(...)`
- Added Analytics ingestion iterators:
  - `iter_analytics_workspace_documents(...)`
  - `iter_analytics_view_documents(..., strategy=\"bulk\" | \"direct\")`
- Added `AnalyticsDataClient.list_rows(...)` for direct row retrieval workflows
- Expanded enterprise-search examples to include Cliq and Analytics ingestion
- Added snippet-backed ingestion playbooks:
  - `docs/ingestion/cliq.md`
  - `docs/ingestion/analytics.md`
  - Canonical sources in `examples/ingestion/cliq_pipeline.py` and `examples/ingestion/analytics_pipeline.py`
- Release engineering:
  - Hardened CI auth-cli error assertions against Typer rich/ANSI output
  - Switched codegen drift commands to `python -m tools.codegen.*` module execution
  - Aligned curated spec drift input set with golden fixtures

## v0.1.2

- Added `zoho.cliq` module with `users`, `chats`, `channels`, `messages`, and `threads` clients
- Added `zoho.analytics` module with `metadata`, `data`, and `bulk` clients
- Added `zoho.writer` module with `documents`, `folders`, and `merge` clients
- Added `zoho.mail` module with `accounts`, `folders`, `messages`, and `threads` clients
- Added new ingestion iterators:
  - `iter_mail_message_documents(...)`
  - `iter_writer_document_documents(...)`
- Added API research notes under `refs/apis/` for Cliq/Analytics/Writer/Mail
- Extended curated codegen snapshots and golden tests for new products
- Expanded docs and README examples for all newly added products and ingestion workflows

## v0.1.1

- Added `zoho.people` module with `forms`, `employees`, and `files` clients
- Added `zoho.sheet` module with `workbooks`, `worksheets`, and `tabular` clients
- Added `zoho.workdrive` module with `files`, `folders`, `search`, `changes`, and `admin` clients
- Added multi-account connection management (`ZohoConnectionProfile`, `client.connections`, `client.for_connection(...)`)
- Added `zoho.ingestion` iterators with checkpoint models for connector workflows
- Added API research notes in `refs/apis/` for People/Sheet/WorkDrive integration requirements
- Added curated spec snapshots and codegen summary tooling for People/Sheet/WorkDrive
- Extended CI codegen drift checks to include curated product snapshots
- Expanded docs and examples for new products, multi-account usage, and ingestion patterns

## v0.1.0

- Added `zoho.creator` module with `meta`, `data`, and `publish` clients
- Added `zoho.projects` module (V3) with `portals`, `projects`, and `tasks` clients
- Added typed Creator/Projects response models for stronger IDE support
- Added product-specific settings (`creator_base_url`, `creator_environment_header`, `projects_base_url`, `projects_default_portal_id`)
- Added Creator/Projects unit tests and integration smoke test scaffolding
- Added codegen expansion:
  - Creator OpenAPI loader and summary tooling
  - Projects live-docs scraper and extracted V3 artifact
- Expanded CI codegen drift job to validate CRM, Creator, and Projects snapshots
- Expanded developer docs and examples for Creator and Projects workflows

## v0.0.1

- Initial async-first Zoho SDK foundation
- Core runtime with typed auth/transport/errors/pagination
- CRM foundation endpoints (records/modules/org/users)
- Token stores: memory/sqlite/redis
- Codegen scaffolding with golden tests
- CI and release workflow setup
