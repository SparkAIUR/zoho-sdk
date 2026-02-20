# Mail Threads API

```python
threads = await client.mail.threads.list(account_id="123456789", start=1, limit=100)
thread = await client.mail.threads.get(account_id="123456789", thread_id="thread_1")
```

Thread actions:

```python
await client.mail.threads.mark_read(account_id="123456789", thread_id="thread_1", is_read=True)
await client.mail.threads.move(account_id="123456789", thread_id="thread_1", folder_id="200")
```
