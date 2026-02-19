# WorkDrive Search API

## Query Search

```python
results = await client.workdrive.search.query(
    term="quarterly report",
    folder_id="folder_123",
    limit=100,
)
print(results.resources)
```
