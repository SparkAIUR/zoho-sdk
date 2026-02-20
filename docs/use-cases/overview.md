# Use Cases

These guides are scenario-driven references built from canonical source files in `examples/`.

## Scenario Map

| Scenario | Primary Guide | Canonical Sources |
|---|---|---|
| FastAPI server-side app + CRM submodules | [FastAPI + CRM](fastapi-crm.md) | `examples/fastapi_crm/main.py` |
| Temporal workflows (on-demand + cron) | [Temporal Workflows](temporal.md) | `examples/temporal/on_demand_worker.py`, `examples/temporal/cron_worker.py` |
| Ingestion workflow orchestration | [Ingestion Workflow](ingestion.md) | `examples/ingestion/pipeline.py`, `examples/ingestion/cliq_pipeline.py`, `examples/ingestion/analytics_pipeline.py` |
| Enterprise search ingestion integration | [Enterprise Search](enterprise-search.md) | `examples/enterprise_search/` |
| Full stack tenant OAuth grants | [FastAPI + Next.js](fullstack-fastapi-nextjs.md) | `examples/fullstack_fastapi_nextjs/` |

## Why Snippet-Backed Docs

- Prevent docs drift by referencing source files directly.
- Keep examples reviewable and reusable in tests/tooling.
- Make updates atomic: edit once in `examples/`, reflected everywhere.

## Operational Notes

- Examples are mock production skeletons, not drop-in deployment templates.
- Keep explicit credentials/config over implicit environment coupling.
- For credential and scope setup, see [Authentication](../authentication.md) and [Credential Setup](../auth-credentials.md).
