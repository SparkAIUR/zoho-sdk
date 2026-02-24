# Repository Guidelines

## Project Structure & Module Organization
- `src/zoho/`: SDK source. Current product modules: `crm`, `creator`, `projects`, `people`, `sheet`, `workdrive`, plus `ingestion` and shared `core`.
- `docs/`: canonical markdown docs source. Scenario playbooks live in `docs/use-cases/`.
- `.sparkify/docs/`: generated Sparkify-ready MDX output (build artifact; do not commit).
- `examples/`: canonical, snippet-backed reference sources used by docs (`--8<--` markers).
- `tools/`: operational/codegen scripts (for example `admin_validate_live.py`, `scopes_sync.py`).
- `refs/docs/`: inception/spec references. `refs/notes/` is private and should not be committed.

## Build, Test, and Development Commands
Use `uv` exclusively for environment, dependency, and build workflows.
- `uv sync --group dev`: install runtime + dev dependencies.
- `uv run ruff format . && uv run ruff check .`: format and lint.
- `uv run mypy`: strict type checks.
- `uv run pytest`: full test suite.
- `uv run pytest tests/docs/test_snippet_references.py`: validate snippet includes/markers.
- `uv run pytest tests/tools/test_render_sparkify_docs.py`: validate Sparkify docs renderer.
- `uv run python tools/render_sparkify_docs.py --source docs --output .sparkify/docs --mkdocs-config mkdocs.yml`: generate Sparkify-ready docs.
- `(cd .sparkify-tool && node packages/cli/dist/bin.js build --docs-dir ../.sparkify/docs --out ../.sparkify/site --site "$DOCS_SITE_URL" --base "" --strict)`: docs build gate (requires a local `.sparkify-tool` checkout of `SparkAIUR/sparkify`).
- `uv run zoho-auth --help`: auth/scope CLI entrypoint.
- `uv run python tools/sync_wiki.py --repo SparkAIUR/zoho-sdk --push`: sync `docs/` into GitHub Wiki (requires wiki to be initialized with a first page).

## Coding Style & Naming Conventions
- Python 3.12+, 4-space indentation, and explicit type hints on public APIs.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Prefer explicit configuration arguments (`client_id`, `client_secret`, etc.) over implicit env-only behavior.
- Use `pydantic` and `pydantic-settings` for typed models/settings.
- Design for performance: lazy-load heavy paths, avoid unnecessary allocations, and make caching behavior explicit and overridable.
- Keep examples in `examples/` and include them into docs via snippet markers.

## Testing Guidelines
- Use `pytest` with async coverage (`pytest-asyncio`) for async clients/workflows.
- Test naming: `tests/test_*.py`; mirror package structure where practical (`tests/crm/`, `tests/core/`, etc.).
- Add golden tests for code generation and regression tests for auth, token caching, retries, and pagination.
- Add/update docs integrity tests when introducing new snippet-backed pages.

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`), scoped when useful (`feat(crm): ...`).
- PRs should include a clear scope and rationale.
- PRs should link relevant spec/context (`refs/docs/specs/...`) when applicable.
- PRs should include test evidence (commands run and results).
- PRs should update `docs/` and `examples/` when public behavior changes.

## Security & Configuration Tips
- Never commit secrets, OAuth tokens, or customer data.
- Redact sensitive fields from logs; support both human-readable and JSON logging modes.
- Keep generated artifacts reproducible and avoid manual edits to generated files.
- For live checks, use read-only admin validation: `uv run python tools/admin_validate_live.py` with `ZOHO_CREDENTIALS_FILE`.
