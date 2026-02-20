# Cliq Ingestion

Use Cliq ingestion iterators for collaboration search indexing with resumable checkpoints.

## Checkpoint Store

```python
--8<-- "examples/ingestion/cliq_pipeline.py:checkpoint_store"
```

## Index Hook

```python
--8<-- "examples/ingestion/cliq_pipeline.py:index_documents"
```

## Channels + Chats + Messages

```python
--8<-- "examples/ingestion/cliq_pipeline.py:channel_chat_job"
```

## Threads

```python
--8<-- "examples/ingestion/cliq_pipeline.py:thread_job"
```

## Runner

```python
--8<-- "examples/ingestion/cliq_pipeline.py:runner"
```

## Notes

- Defaults are metadata-safe (`content=None`, `raw={}`) to minimize sensitive payload leakage.
- Enable richer indexing explicitly using `include_content=True` and `include_raw=True`.
- Persist per-surface checkpoint keys (`cliq_channels`, `cliq_chats`, `cliq_threads`) to support partial retries.
