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
uv run mkdocs build --strict
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
- include usage examples for high-usage APIs
