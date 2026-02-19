# Code Generation

v0.0.1 includes codegen scaffolding to keep upstream compatibility sustainable.

## Inputs

- CRM `json_details.json` (model metadata)
- OpenAPI spec files (endpoint metadata)

## Run Summary Generator

```bash
uv run python tools/codegen/main.py \
  --json-details tests/fixtures/json_details_minimal.json \
  --openapi tests/fixtures/openapi_minimal.json \
  --output /tmp/ir_summary.json
```

## Golden Tests

Golden snapshots are stored in `tests/golden/` and validated by `tests/codegen/`.
This catches unintentional generator behavior drift.
