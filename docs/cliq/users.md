# Cliq Users API

```python
users = await client.cliq.users.list(limit=100)
user = await client.cliq.users.get(user_id="123456789")
```

Create/update:

```python
created = await client.cliq.users.create(data={"email": "dev@example.com", "display_name": "Dev"})
updated = await client.cliq.users.update(user_id="123456789", data={"display_name": "Developer"})
```
