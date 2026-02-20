# Cliq Chats API

```python
chats = await client.cliq.chats.list(limit=100)
members = await client.cliq.chats.list_members(chat_id="chat_id")
```

Conversation controls:

```python
await client.cliq.chats.mute(chat_id="chat_id")
await client.cliq.chats.unmute(chat_id="chat_id")
```
