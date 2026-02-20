# Zoho Cliq API Research

Source:
- https://www.zoho.com/cliq/help/restapi/v2/
- https://oas-download-files-development.zohostratus.com/cliq/cliq-openapi-all.zip

## Product Fit For Ingestion

High-value surfaces for enterprise search and collaboration indexing:
- Channels and channel membership graph
- Direct chats and thread metadata
- Messages (including webhook-posted bot/automation messages)

## Authentication

- OAuth 2.0 with Zoho Accounts domain matching DC.
- Token header format: `Authorization: Zoho-oauthtoken <token>`.
- Scope naming pattern: `ZohoCliq.<resource>.<operation>`.
- Common scopes for our MVP: `ZohoCliq.Users.READ`, `ZohoCliq.Chats.READ`, `ZohoCliq.Channels.READ`, `ZohoCliq.Messages.READ`.

## Base URL and Multi-DC

Docs list DC domains with `/api/v2` base path.
Primary pattern: `https://cliq.zoho.<tld>/api/v2/...`.

SDK requirements:
- DC-aware defaults
- Explicit `cliq_base_url` override
- Preserve optional `/network/{NETWORK_UNIQUE_NAME}` routing for advanced org-specific deployments

## Pagination and Limits

Observed in OAS/docs:
- `limit` + `next_token` on list APIs (users/channels/threads followers)
- time-window filters (`modified_before`, `modified_after`) for some endpoints
- per-endpoint threshold + lock period (for example 20-50 req/min with lock windows)

Connector implication:
- checkpoint can be `next_token` first, with time-window fallbacks
- conservative batching and retries for lock-window handling

## MVP Endpoint Bundle

- Users: list/get/create/update
- Chats: list/members/mute/unmute
- Channels: list/get/create/update/delete/members
- Messages: list/get/post/update/delete
- Threads: followers management and thread state helpers

## Notes For `pipeshub-ai` Ingestion

- Prefer read-only sync from channels/chats/messages first.
- Track message IDs and timestamps for incremental updates.
- Keep tenant-specific connection profiles and least-privilege scopes.
