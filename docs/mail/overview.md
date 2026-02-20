# Mail Overview

`client.mail` supports account, folder, message, and thread APIs.

## Quick Example

```python
accounts = await client.mail.accounts.list()
for account in accounts.result_rows:
    print(account.get("displayName"), account.get("accountId"))
```

## Ingestion Fit

Mail is a first-class ingestion surface for enterprise search pipelines:
- account/folder topology
- message subject/snippet/content
- thread-level grouping
