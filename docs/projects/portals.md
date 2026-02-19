# Portals API

## List Portals

```python
portals = await client.projects.portals.list()
for portal in portals:
    print(portal.id, portal.name)
```

## Get Portal

```python
portal = await client.projects.portals.get(portal_id="12345678")
if portal is not None:
    print(portal.id, portal.name)
```
