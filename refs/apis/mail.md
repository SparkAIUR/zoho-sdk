# Zoho Mail API Research

Source:
- https://www.zoho.com/mail/help/api/overview.html
- https://www.zoho.com/mail/help/api/
- https://www.zoho.com/mail/help/api/using-oauth-2.html
- https://www.zoho.com/mail/help/api/get-all-users-accounts.html
- https://www.zoho.com/mail/help/api/get-all-folder-details.html
- https://www.zoho.com/mail/help/api/get-emails-list.html

## Product Fit For Ingestion

Core enterprise communication ingestion target:
- account and folder topology
- message/thread metadata and content previews
- optional audit/log surfaces for admin-grade compliance indexing

## Authentication

- OAuth 2.0 with Zoho Accounts flow.
- Authorization header: `Authorization: Zoho-oauthtoken <token>`.
- Scope syntax: `ZohoMail.<scope_name>.<operation>`.
- Common scopes for MVP:
  - `ZohoMail.accounts.READ`
  - `ZohoMail.folders.READ`
  - `ZohoMail.messages.READ`
  - `ZohoMail.threads.READ`

## Base URL and API Paths

Observed request pattern:
- `https://mail.zoho.com/api/...`

SDK requirements:
- DC-aware default domains
- explicit `mail_base_url` override
- keep method-specific paths close to docs naming (`/accounts`, `/folders`, `/messages/view`, `/threads`)

## Pagination and Limits

Mail list APIs expose classic pagination:
- `start` (offset-like sequence)
- `limit` (for example max 200 on list emails endpoint)

Connector implication:
- checkpoints should store numeric `start` offset
- optional filters (`folderId`, `status`, `threadId`) should be preserved in checkpoint metadata

## MVP Endpoint Bundle

- Accounts: list/get
- Folders: list/get/create/update/delete
- Messages: list/get/send/move/mark-read/delete
- Threads: list/get/mark-read/move/delete

## Notes For `pipeshub-ai` Ingestion

- Start from account -> folder -> messages hierarchy.
- Normalize message subject/snippet/content as search text.
- Persist checkpoint by `start` and folder/account identifiers per tenant.
