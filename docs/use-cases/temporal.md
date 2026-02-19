# Temporal Workflow Integration

This pattern is for durable background execution where ingestion runs are retried, resumed, and observed through Temporal.

## On-Demand Worker Workflow

Use this when a user/admin triggers a targeted sync for one tenant/module.

### Workflow Input

```python
--8<-- "examples/temporal/on_demand_worker.py:on_demand_request"
```

### Activity (Zoho Read + Checkpoint Return)

```python
--8<-- "examples/temporal/on_demand_worker.py:on_demand_activity"
```

### Workflow Definition

```python
--8<-- "examples/temporal/on_demand_worker.py:on_demand_workflow"
```

### Worker Bootstrap + Trigger

```python
--8<-- "examples/temporal/on_demand_worker.py:on_demand_worker_bootstrap"
```

```python
--8<-- "examples/temporal/on_demand_worker.py:on_demand_start"
```

## Cron Workflow

Use this when ingestion must run on a fixed cadence (for example hourly or nightly).

### Cron Request + Activity

```python
--8<-- "examples/temporal/cron_worker.py:cron_request"
```

```python
--8<-- "examples/temporal/cron_worker.py:cron_activity"
```

### Workflow + Worker + Schedule

```python
--8<-- "examples/temporal/cron_worker.py:cron_workflow"
```

```python
--8<-- "examples/temporal/cron_worker.py:cron_worker_bootstrap"
```

```python
--8<-- "examples/temporal/cron_worker.py:cron_schedule"
```

## Notes

- Keep activities idempotent: retries should not duplicate external writes.
- Persist checkpoints per workflow input (tenant/module/folder).
- Use separate task queues for on-demand and cron workloads to isolate capacity.
