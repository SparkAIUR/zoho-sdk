# Credential Setup (Zoho OAuth)

This guide shows how to obtain the credentials required by this SDK:

- `client_id`
- `client_secret`
- `refresh_token`
- `dc` (data center)

Use official Zoho OAuth flows. For most backend/internal integrations, **Self Client + authorization code flow** is the fastest path.

## 1. Create a Client in Zoho API Console

1. Open [Zoho API Console](https://api-console.zoho.com/).
2. Choose a client type:
   - **Self Client**: best for backend jobs/internal use.
   - **Server-based**: best for multi-user web apps with redirect flow.
3. Create the client and copy values from the **Client Secret** tab:
   - `Client ID` -> `client_id`
   - `Client Secret` -> `client_secret`

Reference:
- https://www.zoho.com/accounts/protocol/oauth-setup.html
- https://www.zoho.com/accounts/protocol/oauth/self-client/overview.html

## 2. Choose CRM Scopes

For CRM features in v0.1.0 (`records`, `modules`, `org`, `users`), a practical starting scope set is:

```text
ZohoCRM.modules.ALL,ZohoCRM.settings.ALL,ZohoCRM.users.ALL,ZohoCRM.org.ALL
```

Adjust scopes down if your app needs less access.

For Creator and Projects features, add product scopes according to your exact endpoints.
Start from the official scope docs and request least privilege:

- Creator: https://www.zoho.com/creator/help/api/v2/oauth-overview.html
- Projects: https://www.zoho.com/projects/help/rest-api/zohoprojectsapi.html

Reference:
- https://www.zoho.com/crm/developer/docs/api/v8/scopes.html

## 3A. Self Client Flow (Recommended for Quick Setup)

1. In your Self Client, open **Generate Code**.
2. Enter scopes (comma-separated), choose short expiry, click **Create**.
3. Copy the generated authorization `code`.
4. Exchange the code for tokens:

```bash
curl --request POST \
  --url "https://accounts.zoho.com/oauth/v2/token" \
  --data "grant_type=authorization_code" \
  --data "client_id=${ZOHO_CLIENT_ID}" \
  --data "client_secret=${ZOHO_CLIENT_SECRET}" \
  --data "code=${ZOHO_GRANT_CODE}"
```

Save:
- `refresh_token` (long-lived; used by this SDK)
- `api_domain`

Reference:
- https://www.zoho.com/accounts/protocol/oauth/self-client/authorization-code-flow.html

## 3B. Server-based Flow (User Authorization)

1. Redirect users to Zoho auth URL with `access_type=offline`.
2. Capture `code` from your callback URL.
3. Exchange code for tokens with `redirect_uri` included.

Reference:
- https://www.zoho.com/crm/developer/docs/api/v8/auth-request.html
- https://www.zoho.com/crm/developer/docs/api/v8/access-refresh.html

## 4. Pick the Correct Data Center (`dc`)

Use the accounts domain matching your Zoho region when generating tokens:

- US: `https://accounts.zoho.com`
- EU: `https://accounts.zoho.eu`
- IN: `https://accounts.zoho.in`
- AU: `https://accounts.zoho.com.au`
- JP: `https://accounts.zoho.jp`
- CA: `https://accounts.zohocloud.ca`
- SA: `https://accounts.zoho.sa`
- CN: `https://accounts.zoho.com.cn`

Set SDK `dc` accordingly (`US`, `EU`, `IN`, `AU`, `JP`, `CA`, `SA`, `CN`).

Reference:
- https://www.zoho.com/crm/developer/docs/api/v8/access-refresh.html

## 5. Configure the SDK

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

Or set env vars:

```bash
export ZOHO_CLIENT_ID="..."
export ZOHO_CLIENT_SECRET="..."
export ZOHO_REFRESH_TOKEN="..."
export ZOHO_DC="US"
export ZOHO_ENVIRONMENT="production"
```
