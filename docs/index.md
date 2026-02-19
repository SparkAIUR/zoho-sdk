# zoho SDK

`zoho` is an async-first Python SDK for Zoho APIs, focused on strong typing, lazy loading, and high-performance async execution.

## Design Goals

- Keep high-usage flows simple and explicit.
- Deliver strong typing and IDE guidance.
- Support single-user scripts and large multi-worker environments.
- Keep upstream compatibility sustainable through code generation.

## v0.1.0 Scope

- Core runtime: auth, token store, transport, errors, pagination, logging
- CRM APIs: records, modules, org, users
- Creator APIs: meta, data, publish
- Projects V3 APIs: portals, projects, tasks
- Codegen tooling with golden tests and projects-doc extraction
- Strict CI gates and robust documentation
