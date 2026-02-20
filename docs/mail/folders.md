# Mail Folders API

```python
folders = await client.mail.folders.list(account_id="123456789")
folder = await client.mail.folders.get(account_id="123456789", folder_id="100")
```

CRUD:

```python
created = await client.mail.folders.create(account_id="123456789", folder_name="Vendors")
await client.mail.folders.update(account_id="123456789", folder_id="100", folder_name="Vendors-2026")
await client.mail.folders.delete(account_id="123456789", folder_id="100")
```
