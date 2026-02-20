# Analytics Bulk API

Use bulk endpoints for ingestion-scale imports/exports and asynchronous job tracking.

```python
export_job = await client.analytics.bulk.export_data(
    workspace_id="workspace_id",
    view_id="view_id",
    config={"format": "json"},
)

status = await client.analytics.bulk.get_export_job(
    workspace_id="workspace_id",
    job_id="job_id",
)
```
