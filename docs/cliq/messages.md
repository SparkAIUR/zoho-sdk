# Cliq Messages API

```python
messages = await client.cliq.messages.list(chat_id="chat_id", limit=100)
message = await client.cliq.messages.get(chat_id="chat_id", message_id="msg_id")
```

Posting and edits:

```python
await client.cliq.messages.post_to_channel(
    channel_unique_name="engineering",
    data={"text": "Nightly sync complete"},
)
await client.cliq.messages.update(
    chat_id="chat_id",
    message_id="msg_id",
    data={"text": "Updated content"},
)
```
