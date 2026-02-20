# Analytics Ingestion

Use Analytics ingestion iterators for metadata graph indexing and view-row extraction.

## Checkpoint Store

```python
--8<-- "examples/ingestion/analytics_pipeline.py:checkpoint_store"
```

## Index Hook

```python
--8<-- "examples/ingestion/analytics_pipeline.py:index_documents"
```

## Workspace Graph (Organizations, Workspaces, Views)

```python
--8<-- "examples/ingestion/analytics_pipeline.py:workspace_graph_job"
```

## View Rows (Dual Strategy: `bulk` or `direct`)

```python
--8<-- "examples/ingestion/analytics_pipeline.py:view_rows_job"
```

## Runner

```python
--8<-- "examples/ingestion/analytics_pipeline.py:runner"
```

## Notes

- Pass `ZANALYTICS-ORGID` explicitly in `headers`.
- `strategy="bulk"` is best for large exports and resumable polling.
- `strategy="direct"` is useful for incremental low-latency reads.
- Defaults are metadata-safe (`content=None`, `raw={}`) and can be overridden per iterator.
