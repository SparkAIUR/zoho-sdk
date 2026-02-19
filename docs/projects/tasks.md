# Tasks API

## List Tasks

```python
tasks = await client.projects.tasks.list(
    portal_id="12345678",
    project_id="4000000070029",
    page=1,
    per_page=100,
)
print(tasks[0].id if tasks else None)
```

## Get / Create / Update / Close Task

```python
task = await client.projects.tasks.get(
    portal_id="12345678",
    project_id="4000000070029",
    task_id="4000000123001",
)
if task is not None:
    print(task.id, task.name)

await client.projects.tasks.create(
    portal_id="12345678",
    project_id="4000000070029",
    data={"name": "Add API smoke tests"},
)

await client.projects.tasks.update(
    portal_id="12345678",
    project_id="4000000070029",
    task_id="4000000123001",
    data={"name": "Add API + load smoke tests"},
)

await client.projects.tasks.close(
    portal_id="12345678",
    project_id="4000000070029",
    task_id="4000000123001",
)
```
