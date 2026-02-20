# Analytics Overview

`client.analytics` targets Zoho Analytics REST API v2 with typed helpers for metadata, data-row operations, and bulk jobs.

## Quick Example

```python
orgs = await client.analytics.metadata.list_organizations()
for org in orgs.result_rows:
    print(org.get("orgName"), org.get("orgId"))
```

## Important Header

Many endpoints require `ZANALYTICS-ORGID`. Pass explicitly via `headers`:

```python
rows = await client.analytics.data.create_rows(
    workspace_id="...",
    view_id="...",
    config={"rows": [{"Email": "alex@example.com"}]},
    headers={"ZANALYTICS-ORGID": "123456789"},
)
```
