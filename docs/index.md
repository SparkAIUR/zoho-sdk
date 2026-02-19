# zoho SDK

`zoho` is an async-first Python SDK for Zoho APIs, focused on strong typing, lazy loading, and high-throughput connector workloads.

## Design Goals

- Keep high-usage flows simple and explicit.
- Deliver strong typing and IDE guidance.
- Support singleton apps and multi-tenant worker fleets.
- Keep upstream compatibility sustainable through code generation.
- Enable ingestion-first workflows for enterprise search connectors.

## v0.1.1 Scope

- Core runtime: auth, token store, transport, errors, pagination, logging
- Multi-account connection manager (`connections`, `for_connection`)
- Product modules:
  - CRM (`records`, `modules`, `org`, `users`)
  - Creator (`meta`, `data`, `publish`)
  - Projects V3 (`portals`, `projects`, `tasks`)
  - People (`forms`, `employees`, `files`)
  - Sheet (`workbooks`, `worksheets`, `tabular`)
  - WorkDrive (`files`, `folders`, `search`, `changes`, `admin`)
- Ingestion iterators under `zoho.ingestion`
- Codegen tooling with golden tests and curated spec snapshots
- Strict CI gates and robust documentation
