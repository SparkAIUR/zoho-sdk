# Projects API

## List Projects

```python
projects = await client.projects.projects.list(
    portal_id="12345678",
    page=1,
    per_page=50,
)
print(projects[0].id if projects else None)
```

## Get Project

```python
project = await client.projects.projects.get(
    portal_id="12345678",
    project_id="4000000070029",
)
if project is not None:
    print(project.id, project.name)
```

## Create / Update / Trash

```python
created = await client.projects.projects.create(
    portal_id="12345678",
    data={"name": "SDK Rollout"},
)
print(created.status)

await client.projects.projects.update(
    portal_id="12345678",
    project_id="4000000070029",
    data={"name": "SDK Rollout - Phase 2"},
)

await client.projects.projects.trash(
    portal_id="12345678",
    project_id="4000000070029",
)
```
