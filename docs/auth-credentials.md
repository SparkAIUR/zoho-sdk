# Credential Setup (Zoho OAuth)

This guide shows how to obtain the credentials required by this SDK:

- `client_id`
- `client_secret`
- `refresh_token`
- `dc` (data center)

Use official Zoho OAuth flows. For most backend/internal integrations, **Self Client + authorization code flow** is the fastest path.

## 1. Create a Client in Zoho API Console

1. Open [Zoho API Console](https://api-console.zoho.com/).
2. Choose client type:
   - **Self Client** for backend jobs/internal integrations.
   - **Server-based** for multi-user web redirect flows.
3. Create the client and collect:
   - `Client ID` -> `client_id`
   - `Client Secret` -> `client_secret`

References:
- https://www.zoho.com/accounts/protocol/oauth-setup.html
- https://www.zoho.com/accounts/protocol/oauth/self-client/overview.html

## 2. Choose Product Scopes

Start with least privilege and only add scopes needed by your endpoints.

Use the generated scope matrix for SDK-supported products:

- [Zoho OAuth Scope Catalog](scopes.md)

### CRM (current core + existing modules)

```text
ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL,ZohoCRM.org.ALL
```

### People (examples from docs)

```text
ZOHOPEOPLE.forms.ALL,ZOHOPEOPLE.form.READ
```

### WorkDrive (examples from docs)

```text
WorkDrive.team.ALL,WorkDrive.files.READ,WorkDrive.files.UPDATE
```

### Sheet

Use the scopes shown in the Zoho Sheet API auth section for the exact endpoints you plan to call.

References:
- CRM: https://www.zoho.com/crm/developer/docs/api/v8/scopes.html
- People: https://www.zoho.com/people/api/oauth.html
- Sheet: https://sheet.zoho.com/help/api/v2/
- WorkDrive: https://workdrive.zoho.com/apidocs/v1/overview

## 3A. Self Client Flow (Recommended)

1. In Self Client, open **Generate Code**.
2. Enter scopes (comma-separated), short expiry, then create.
3. Copy authorization `code`.
4. Exchange code for tokens:

```bash
curl --request POST \
  --url "https://accounts.zoho.com/oauth/v2/token" \
  --data "grant_type=authorization_code" \
  --data "client_id=${ZOHO_CLIENT_ID}" \
  --data "client_secret=${ZOHO_CLIENT_SECRET}" \
  --data "code=${ZOHO_GRANT_CODE}"
```

Save:
- `refresh_token` (long-lived, SDK uses this)
- `api_domain`

## 3B. Server-Based Flow

1. Redirect users to Zoho auth URL with `access_type=offline`.
2. Capture `code` from callback URL.
3. Exchange code for tokens with `redirect_uri` included.

References:
- https://www.zoho.com/crm/developer/docs/api/v8/auth-request.html
- https://www.zoho.com/crm/developer/docs/api/v8/access-refresh.html

## 4. Pick Correct Data Center (`dc`)

Use matching accounts domain for token generation:

- US: `https://accounts.zoho.com`
- EU: `https://accounts.zoho.eu`
- IN: `https://accounts.zoho.in`
- AU: `https://accounts.zoho.com.au`
- JP: `https://accounts.zoho.jp`
- CA: `https://accounts.zohocloud.ca`
- SA: `https://accounts.zoho.sa`
- CN: `https://accounts.zoho.com.cn`

Set SDK `dc` accordingly.

## 5. Configure SDK

```python
from zoho import Zoho

client = Zoho.from_credentials(
    client_id="1000....",
    client_secret="....",
    refresh_token="1000....",
    dc="US",
    environment="production",
)
```

Or via env vars:

```bash
export ZOHO_CLIENT_ID="..."
export ZOHO_CLIENT_SECRET="..."
export ZOHO_REFRESH_TOKEN="..."
export ZOHO_DC="US"
export ZOHO_ENVIRONMENT="production"
```
