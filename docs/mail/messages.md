# Mail Messages API

```python
messages = await client.mail.messages.list(
    account_id="123456789",
    folder_id="100",
    start=1,
    limit=200,
)
```

Read/send/move:

```python
message = await client.mail.messages.get(account_id="123456789", message_id="999")
await client.mail.messages.send(
    account_id="123456789",
    from_address="ops@example.com",
    to=["team@example.com"],
    subject="Daily report",
    content="Attached is the latest report.",
)
await client.mail.messages.move(account_id="123456789", message_id="999", folder_id="200")
```
