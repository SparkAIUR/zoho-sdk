# Code Generation

Codegen tooling keeps the SDK aligned with upstream Zoho changes while keeping diffs reviewable.

## Inputs

- CRM `json_details.json` (model metadata)
- OpenAPI spec files (endpoint metadata)
- Creator OpenAPI documents
- Projects V3 API docs HTML (extracted into internal JSON spec)
- Curated People/Sheet/WorkDrive spec snapshots

## CRM Summary Generator

```bash
uv run python tools/codegen/main.py \
  --json-details tests/fixtures/json_details_minimal.json \
  --openapi tests/fixtures/openapi_minimal.json \
  --output /tmp/ir_summary.json
```

## Creator Summary Generator

```bash
uv run python tools/codegen/creator_summary.py \
  --openapi tests/fixtures/creator_openapi_minimal.json \
  --output /tmp/creator_summary.json
```

## Projects Extractor

```bash
# Parse a local fixture
uv run python tools/codegen/projects_extract.py \
  --html tests/fixtures/projects/api_docs_sample.html \
  --output /tmp/projects_extracted_mvp.json

# Parse live docs
uv run python tools/codegen/projects_extract.py \
  --all \
  --output tools/specs/projects_v3_extracted.json
```

## Curated Product Summary

```bash
uv run python tools/codegen/curated_summary.py \
  --spec tools/specs/people_v1_curated.json \
  --spec tools/specs/sheet_v2_curated.json \
  --spec tools/specs/workdrive_v1_curated.json \
  --output /tmp/curated_summary.json
```

## Golden Tests

Golden snapshots are stored in `tests/golden/` and validated by `tests/codegen/`.
This catches unintentional generator behavior drift.
