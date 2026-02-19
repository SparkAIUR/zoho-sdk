# Auth Helper CLI

Use `zoho-auth` for admin-friendly OAuth helper workflows.

The command always expects a credentials file from `ZOHO_CREDENTIALS_FILE` (or `--credentials-file`) and loads it with `dotenv`.

## Exchange Grant Code For Tokens

```bash
export ZOHO_CREDENTIALS_FILE=refs/notes/zoho-live.env
uv run zoho-auth exchange-token --grant-code "<grant-code>"
```

Add `--show-secrets` only when you explicitly need raw tokens in output.

## Build Self-Client Grant Code Request (Template Mode)

```bash
uv run zoho-auth grant-code \
  --self-client-id "1000..." \
  --scopes "ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL,ZohoCRM.org.ALL" \
  --expiry 10 \
  --description "Evaluation of Zoho SDK"
```

Template mode prints:

- target endpoint
- request payload
- ready-to-edit `curl` command skeleton

## Execute Self-Client Grant Code Request

```bash
uv run zoho-auth grant-code \
  --self-client-id "1000..." \
  --scope "ZohoCRM.modules.ALL" \
  --execute \
  --session-cookie "<session cookie>" \
  --x-zcsrf-token "<token>"
```

`--execute` requires active API Console session credentials. By default, response output is redacted for token-like fields.
