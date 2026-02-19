# Code generation

## Why codegen

Zoho APIs are large, and Zoho frequently ships changes. Hand-maintaining a full SDK is not realistic.

Goals:
- generate endpoint methods + models
- keep changes reviewable (small diffs)
- allow product-by-product onboarding

## Inputs

### CRM
- OAS files (endpoints + schema)
- `json_details.json` (model metadata used by Zoho’s Python SDK)

### Creator
- OAS downloads from Zoho Creator docs

### Analytics
- OAS repository (v2 data API) + docs

### Projects
- Extracted spec from docs (until official OAS exists)

## Intermediate Representation (IR)

Build a normalized IR used by all generators:

- `Product`
  - `name`
  - `api_version`
  - `regions`
  - `endpoints: list[Endpoint]`
  - `models: list[Model]`

- `Endpoint`
  - `method`, `path`, `operation_id`
  - `request_model`, `response_model`
  - `pagination` (none/page/cursor)
  - `auth` (oauth2 + required scopes)
  - `errors` (status code mapping)

- `Model`
  - `name`, `namespace`
  - `fields: list[Field]`
  - `docstring`

- `Field`
  - `name` (python identifier)
  - `wire_name` (JSON key)
  - `type_ref`
  - `required`, `nullable`
  - `operations_supported` (for CRM: request/response supported flags)

## Generators

### Models generator
- Emit Pydantic v2 models
- Preserve wire names using `Field(alias="...")`
- Use snake_case field names by default but keep a “compat mode” to preserve original casing where helpful

### Endpoints generator
- Emit service classes grouped by tag/module
- Each method calls shared transport and parses responses into models
- Provide “raw response” option for power users

### Formatting & linting
- Run `ruff format` + `ruff check` on generated code
- Avoid expensive runtime imports in generated modules

## CRM json_details ingestion notes

`json_details.json` is a mapping:
- key: fully qualified class name
- value: dict of fields with metadata such as:
  - request_supported/response_supported (ops)
  - type, spec_type, structure, structure_name, sub_type
  - nullable/required/unique hints

We parse this into the IR:
- treat each json_details class as a `Model`
- derive `Field.type_ref` from `type` and `sub_type`
- store the supported operations metadata (optional; useful for validation)

## Golden tests

- Store “golden” generated files in `tests/golden/`
- In CI: regenerate and diff; fail if drift exists
- Enables predictable review of spec changes

## Release workflow

1. Update spec inputs (OAS + json_details).
2. Run generator.
3. Run unit tests + integration smoke tests.
4. Publish.

