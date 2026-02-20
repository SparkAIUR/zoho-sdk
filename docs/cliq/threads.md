# Cliq Threads API

```python
followers = await client.cliq.threads.list_followers(thread_id="thread_id", limit=50)
await client.cliq.threads.add_followers(thread_id="thread_id", user_ids=["u1", "u2"])
```

Thread state:

```python
await client.cliq.threads.close(thread_id="thread_id")
await client.cliq.threads.reopen(thread_id="thread_id")
```
