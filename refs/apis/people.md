# Zoho People API Research

Source:
- https://www.zoho.com/people/api/overview.html
- https://www.zoho.com/people/api/oauth.html
- https://www.zoho.com/people/api/oauth-steps.html
- https://www.zoho.com/people/api/api-limits.html
- https://www.zoho.com/people/api/forms-api/fetch-forms.html

## Product Fit For Ingestion

High-value datasets for enterprise search and user profile enrichment:
- Forms and custom records
- Employee directory records
- Files attached to HR records

## Authentication

- OAuth 2.0 authorization-code flow.
- Access token expiry is typically 1 hour.
- Refresh token is long-lived until revoked.
- Scope naming pattern: `ZOHOPEOPLE.<resource>.<operation>`.
- Example scope from docs: `ZOHOPEOPLE.forms.ALL` and per-endpoint scope examples such as `ZOHOPEOPLE.form.READ`.

## Base URL and Domains

Observed examples use `https://people.zoho.com/people/api/...`.
Multi-DC is relevant; token issuance and API domain must remain in the same DC unless Multi-DC is enabled for client credentials.

## Rate Limits and Lock Behavior

Global plan quotas are documented by plan tier (daily limits).
Endpoint pages also mention threshold lock behavior (example on forms endpoint):
- Threshold limit: 30 requests
- Lock period: 5 minutes

Implication for SDK:
- Connector iterators should keep conservative batch sizes.
- Implement retry/backoff respecting lock windows.

## Response and Data Shape

- Common payload pattern includes nested `response.result` arrays.
- Envelope may vary by endpoint; parser should be permissive (`extra=allow`).

## MVP Endpoint Bundle

- Forms metadata: list forms, list fields
- Forms records: list/search/create/update
- Employees: list/get/create/update
- Files: list/get/create/delete (metadata-oriented first)

## Integration Risks

- People APIs contain mixed naming conventions across V1/V2/V3 docs.
- Some endpoint names/paths in docs are operation-name driven, not always REST-homogeneous.
- Keep `people_base_url` explicit override and allow raw parameter passthrough.

## Notes For `pipeshub-ai` Ingestion

- Primary crawl should start from forms/employees with incremental record polling.
- Persist checkpoint by `offset` and last observed modified timestamp.
- Keep per-connection scopes narrow (least privilege) and use one connection profile per tenant.
