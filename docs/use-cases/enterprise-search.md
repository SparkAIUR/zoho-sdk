# Enterprise Search Ingestion Integration

This pattern maps `zoho.ingestion` batches into search-friendly payloads for downstream systems.

## Shared Input Shape

All adapters consume `IngestionDocument` records emitted by:

- `iter_crm_documents(...)`
- `iter_people_form_documents(...)`
- `iter_sheet_worksheet_documents(...)`
- `iter_workdrive_recent_documents(...)`

## Oynx Integration

### Contract

```python
--8<-- "examples/enterprise_search/oynx/adapter.py:oynx_contract"
```

### Mapper

```python
--8<-- "examples/enterprise_search/oynx/adapter.py:oynx_mapper"
```

### Batch Push

```python
--8<-- "examples/enterprise_search/oynx/adapter.py:oynx_push"
```

### Runner

```python
--8<-- "examples/enterprise_search/pipeline.py:oynx_runner"
```

## Pipeshub AI Integration

### Contract

```python
--8<-- "examples/enterprise_search/pipeshub_ai/adapter.py:pipeshub_contract"
```

### Mapper

```python
--8<-- "examples/enterprise_search/pipeshub_ai/adapter.py:pipeshub_mapper"
```

### Batch Upsert

```python
--8<-- "examples/enterprise_search/pipeshub_ai/adapter.py:pipeshub_push"
```

### Runner

```python
--8<-- "examples/enterprise_search/pipeline.py:pipeshub_runner"
```

## Notes

- Keep adapter payloads explicit and tenant-aware.
- Avoid indexing secrets or highly sensitive fields from `raw` without filtering.
- Preserve source-specific `updated_at` and checkpoint state for incremental sync quality.
