# Contributing

## Setup

```bash
uv sync --group dev
```

## Local Quality Gates

```bash
uv run ruff format .
uv run ruff check .
uv run mypy
uv run pytest
uv run pytest tests/docs/test_snippet_references.py
uv run mkdocs build --strict
```

## Codegen Drift Checks

```bash
uv run python tools/codegen/main.py \
  --json-details tests/fixtures/json_details_minimal.json \
  --openapi tests/fixtures/openapi_minimal.json \
  --output /tmp/ir_summary.json
diff -u tests/golden/ir_summary.json /tmp/ir_summary.json

uv run python tools/codegen/creator_summary.py \
  --openapi tests/fixtures/creator_openapi_minimal.json \
  --output /tmp/creator_summary.json
diff -u tests/golden/creator_summary.json /tmp/creator_summary.json

uv run python tools/codegen/projects_extract.py \
  --html tests/fixtures/projects/api_docs_sample.html \
  --output /tmp/projects_extracted_mvp.json
diff -u tests/golden/projects_extracted_mvp.json /tmp/projects_extracted_mvp.json

uv run python tools/codegen/curated_summary.py \
  --spec tools/specs/people_v1_curated.json \
  --spec tools/specs/sheet_v2_curated.json \
  --spec tools/specs/workdrive_v1_curated.json \
  --spec tools/specs/cliq_v2_curated.json \
  --spec tools/specs/analytics_v2_curated.json \
  --spec tools/specs/writer_v1_curated.json \
  --spec tools/specs/mail_v1_curated.json \
  --output /tmp/curated_summary.json
diff -u tests/golden/curated_summary.json /tmp/curated_summary.json

uv run python tools/scopes_sync.py
uv run zoho-auth --help
```

## Commit Style

Use conventional commits, for example:
- `feat(crm): add records list iterator`
- `fix(auth): handle missing api_domain in token response`
- `docs(readme): add explicit credentials example`

## Documentation Expectations

When public behavior changes:
- update `README.md`
- update or add pages under `docs/`
- update canonical use-case snippets under `examples/` (docs pull from these files)
- include usage examples for high-usage APIs

## Admin Credential Validation

Use the live validator before sharing credential onboarding changes:

```bash
export ZOHO_CREDENTIALS_FILE=refs/notes/zoho-live.env
uv run python tools/admin_validate_live.py
```
