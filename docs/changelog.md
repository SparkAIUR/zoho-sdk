# Changelog

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
