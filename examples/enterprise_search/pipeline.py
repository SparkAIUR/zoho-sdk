"""Enterprise search ingestion runners for Oynx and Pipeshub AI."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from typing import Literal

from zoho import Zoho
from zoho.ingestion import (
    iter_analytics_view_documents,
    iter_cliq_chat_documents,
    iter_crm_documents,
    iter_mail_message_documents,
    iter_workdrive_recent_documents,
    iter_writer_document_documents,
)
from zoho.ingestion.models import IngestionDocument

PushOynxBatch = Callable[[Sequence[IngestionDocument], str, str, str], Awaitable[None]]
UpsertPipeshubBatch = Callable[[Sequence[IngestionDocument], str, str, str], Awaitable[None]]


# --8<-- [start:oynx_runner]
async def run_oynx_sync(
    client: Zoho,
    *,
    tenant_id: str,
    endpoint: str,
    api_key: str,
    push_batch: PushOynxBatch,
) -> None:
    async for batch in iter_crm_documents(
        client,
        modules=["Leads", "Contacts", "Accounts"],
        page_size=200,
        max_pages_per_module=25,
    ):
        await push_batch(
            batch.documents,
            endpoint,
            api_key,
            tenant_id,
        )


# --8<-- [end:oynx_runner]


# --8<-- [start:pipeshub_runner]
async def run_pipeshub_sync(
    client: Zoho,
    *,
    dataset: str,
    endpoint: str,
    api_key: str,
    upsert_batch: UpsertPipeshubBatch,
    cliq_max_pages: int = 25,
    analytics_org_id: str = "123456789",
    analytics_workspace_id: str = "workspace_123",
    analytics_view_id: str = "view_123",
    analytics_strategy: Literal["bulk", "direct"] = "bulk",
) -> None:
    async for batch in iter_workdrive_recent_documents(
        client,
        folder_id="folder_123",
        page_size=200,
        max_pages=50,
    ):
        await upsert_batch(
            batch.documents,
            endpoint,
            api_key,
            dataset,
        )

    async for batch in iter_cliq_chat_documents(
        client,
        include_messages=True,
        page_size=200,
        max_pages=cliq_max_pages,
    ):
        await upsert_batch(
            batch.documents,
            endpoint,
            api_key,
            dataset,
        )

    async for batch in iter_analytics_view_documents(
        client,
        workspace_id=analytics_workspace_id,
        view_id=analytics_view_id,
        strategy=analytics_strategy,
        headers={"ZANALYTICS-ORGID": analytics_org_id},
        page_size=200,
        max_pages=25 if analytics_strategy == "direct" else None,
        max_poll_attempts=10,
        poll_interval_seconds=0.5,
    ):
        await upsert_batch(
            batch.documents,
            endpoint,
            api_key,
            dataset,
        )

    async for batch in iter_writer_document_documents(
        client,
        folder_id="writer_folder_123",
        page_size=200,
        max_pages=25,
    ):
        await upsert_batch(
            batch.documents,
            endpoint,
            api_key,
            dataset,
        )

    async for batch in iter_mail_message_documents(
        client,
        account_id="mail_account_123",
        folder_id="mail_folder_123",
        page_size=200,
        max_pages=25,
    ):
        await upsert_batch(
            batch.documents,
            endpoint,
            api_key,
            dataset,
        )


# --8<-- [end:pipeshub_runner]
