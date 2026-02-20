# Auth Helper CLI

Use `zoho-auth` for admin-friendly OAuth helper workflows.

`exchange-token` and `grant-code` expect a credentials file from `ZOHO_CREDENTIALS_FILE` (or `--credentials-file`) and load it with `dotenv`.

## Interactive Scope Builder

Build a scope set interactively:

```bash
uv run zoho-auth scope-builder
```

Pre-set options with flags (prompts fill the rest):

```bash
uv run zoho-auth scope-builder \
  --product CRM \
  --product WorkDrive \
  --product Mail \
  --product Writer \
  --access read \
  --include-common \
  --format env
```

For fully scripted usage:

```bash
uv run zoho-auth scope-builder \
  --product CRM \
  --product People \
  --product Cliq \
  --product Analytics \
  --access write \
  --no-interactive \
  --format json \
  --output-file /tmp/zoho_scopes.json
```

Validation notes:

- Scope tokens are validated for allowed characters (letters, numbers, `.`, `_`, spaces).
- Template placeholders like `ZohoCRM.modules.{module}.READ` are rejected as invalid tokens.
- Zoho API Console may still reject combinations when a service is not configured for your org.

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
