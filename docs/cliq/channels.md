# Cliq Channels API

```python
channels = await client.cliq.channels.list(limit=100)
channel = await client.cliq.channels.get(channel_id="channel_id")
```

CRUD:

```python
created = await client.cliq.channels.create(data={"name": "eng-api", "level": "team"})
updated = await client.cliq.channels.update(channel_id="channel_id", data={"description": "API Team"})
await client.cliq.channels.delete(channel_id="channel_id")
```

Members:

```python
await client.cliq.channels.add_members(channel_id="channel_id", user_ids=["u1", "u2"])
await client.cliq.channels.remove_members(channel_id="channel_id", user_ids=["u2"])
```
