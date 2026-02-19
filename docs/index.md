# zoho SDK

`zoho` is an async-first Python SDK for Zoho APIs, starting with a CRM-focused foundation.

## Design Goals

- Keep high-usage flows simple and explicit.
- Deliver strong typing and IDE guidance.
- Support single-user scripts and large multi-worker environments.
- Keep upstream compatibility sustainable through code generation.

## v0.0.1 Scope

- Core runtime: auth, token store, transport, errors, pagination, logging
- CRM foundation APIs: records, modules, org, users
- Codegen scaffolding and golden tests
- Strict CI gates and robust documentation
