# Analytics Metadata API

```python
workspaces = await client.analytics.metadata.list_workspaces()
views = await client.analytics.metadata.list_views(workspace_id="workspace_id")
view = await client.analytics.metadata.get_view(view_id="view_id")
```

Dashboards and metadata details:

```python
dashboards = await client.analytics.metadata.list_dashboards(owned=True)
meta = await client.analytics.metadata.get_metadata_details()
```
