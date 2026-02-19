# Sheet Overview

`zoho.sheet` provides workbook, worksheet, and tabular record APIs.

## Initialize

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="...",
    client_secret="...",
    refresh_token="...",
    sheet_base_url="https://sheet.zoho.com",  # optional override
)
```

## Subclients

- `client.sheet.workbooks`
- `client.sheet.worksheets`
- `client.sheet.tabular`
