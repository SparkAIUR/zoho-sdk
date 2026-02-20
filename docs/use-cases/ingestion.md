# Ingestion Workflow

This pattern is for enterprise ingestion pipelines that need resumable checkpoints and predictable batch execution.

## Checkpoint Persistence

```python
--8<-- "examples/ingestion/pipeline.py:checkpoint_store"
```

## Indexing Hook

```python
--8<-- "examples/ingestion/pipeline.py:index_documents"
```

Replace `index_documents(...)` with your actual sink (database, queue, or search index).

## CRM Job

```python
--8<-- "examples/ingestion/pipeline.py:crm_job"
```

## Multi-Source Job (People + Sheet + WorkDrive)

```python
--8<-- "examples/ingestion/pipeline.py:multi_source_job"
```

## Cliq Job (Channels, Chats, Threads)

```python
--8<-- "examples/ingestion/cliq_pipeline.py:channel_chat_job"
```

```python
--8<-- "examples/ingestion/cliq_pipeline.py:thread_job"
```

## Analytics Job (Workspace Graph + View Rows)

```python
--8<-- "examples/ingestion/analytics_pipeline.py:workspace_graph_job"
```

```python
--8<-- "examples/ingestion/analytics_pipeline.py:view_rows_job"
```

## Runner

```python
--8<-- "examples/ingestion/pipeline.py:runner"
```

## Notes

- Persist checkpoint updates after each successful batch.
- Keep source-specific checkpoint keys (`crm`, `people`, `sheet`, `workdrive`).
- Bound pages per run (`max_pages`) to control execution time and memory pressure.
- For Cliq and Analytics, keep separate checkpoint namespaces per source and strategy.
