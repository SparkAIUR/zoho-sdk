# Repository Guidelines

## Project Structure & Module Organization
- `src/zoho/`: SDK source code. Keep public imports ergonomic (`from zoho import ...`, `from zoho.crm import ...`).
- `docs/`: user-facing documentation (MkDocs source).
- `refs/docs/`: project inception/spec references; treat as design inputs.
- `refs/notes/`: private working notes (non-public; do not commit).
- As the SDK grows, keep product code under `src/zoho/<product>/` (for example `crm`, `creator`, `analytics`, `projects`) and place generated code in clear `generated/` subpackages.

## Build, Test, and Development Commands
Use `uv` exclusively for environment, dependency, and build workflows.
- `uv sync`: install/update dependencies from `pyproject.toml` and `uv.lock`.
- `uv run python -c "import zoho"`: quick import smoke test.
- `uv build`: build wheel/sdist using `pyproject.toml` as source of truth.
- `uv run pytest`: run test suite (unit, async, and integration tests).
- `uv run ruff check .` and `uv run ruff format .`: lint and format.

## Coding Style & Naming Conventions
- Python 3.12+, 4-space indentation, and explicit type hints on public APIs.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Prefer explicit configuration arguments (`client_id`, `client_secret`, etc.) over implicit env-only behavior.
- Use `pydantic` and `pydantic-settings` for typed models/settings.
- Design for performance: lazy-load heavy paths, avoid unnecessary allocations, and make caching behavior explicit and overridable.
- Add concise doc examples on high-usage classes/methods.

## Testing Guidelines
- Use `pytest` with async coverage (`pytest-asyncio`) for async clients/workflows.
- Test naming: `tests/test_*.py`; mirror package structure where practical.
- Add golden tests for code generation and regression tests for auth, token caching, retries, and pagination.
- Prioritize strong coverage for core runtime paths before adding new public APIs.

## Commit & Pull Request Guidelines
- Current history is minimal (`Initial commit`), so adopt Conventional Commits going forward (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- PRs should include a clear scope and rationale.
- PRs should link the relevant issue/spec reference (for example `refs/docs/specs/...`).
- PRs should include test evidence (commands run and results).
- PRs should update `docs/` when public APIs or behavior change.

## Security & Configuration Tips
- Never commit secrets, OAuth tokens, or customer data.
- Redact sensitive fields from logs; support both human-readable and JSON logging modes.
- Keep generated artifacts reproducible and avoid manual edits to generated files.
