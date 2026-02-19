"""Temporal on-demand workflow example for Zoho CRM ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.common import RetryPolicy
from temporalio.worker import Worker

from zoho import Zoho
from zoho.ingestion import iter_crm_module_documents
from zoho.ingestion.models import IngestionCheckpoint


# --8<-- [start:on_demand_request]
@dataclass(slots=True)
class OnDemandRequest:
    module: str
    connection_name: str = "default"
    page_size: int = 200
    checkpoint: dict[str, Any] | None = None
# --8<-- [end:on_demand_request]


# --8<-- [start:on_demand_activity]
@activity.defn
async def ingest_crm_module_activity(request: OnDemandRequest) -> dict[str, Any]:
    """Pull one bounded batch of CRM records and return the next checkpoint."""

    client = Zoho.from_credentials(
        client_id="${ZOHO_CLIENT_ID}",
        client_secret="${ZOHO_CLIENT_SECRET}",
        refresh_token="${ZOHO_REFRESH_TOKEN}",
    )

    checkpoint = (
        IngestionCheckpoint.model_validate(request.checkpoint) if request.checkpoint else None
    )

    documents_seen = 0
    next_checkpoint: IngestionCheckpoint | None = checkpoint

    try:
        async for batch in iter_crm_module_documents(
            client,
            module=request.module,
            connection_name=request.connection_name,
            page_size=request.page_size,
            checkpoint=checkpoint,
            max_pages=1,
        ):
            documents_seen += len(batch.documents)
            next_checkpoint = batch.checkpoint

        return {
            "module": request.module,
            "documents_seen": documents_seen,
            "next_checkpoint": (
                next_checkpoint.model_dump(mode="python") if next_checkpoint else None
            ),
        }
    finally:
        await client.close()
# --8<-- [end:on_demand_activity]


# --8<-- [start:on_demand_workflow]
@workflow.defn
class OnDemandCRMIngestionWorkflow:
    @workflow.run
    async def run(self, request: OnDemandRequest) -> dict[str, Any]:
        return await workflow.execute_activity(
            ingest_crm_module_activity,
            request,
            start_to_close_timeout=300,
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
# --8<-- [end:on_demand_workflow]


# --8<-- [start:on_demand_worker_bootstrap]
async def run_worker() -> None:
    temporal_client = await Client.connect("localhost:7233")

    worker = Worker(
        temporal_client,
        task_queue="zoho-on-demand",
        workflows=[OnDemandCRMIngestionWorkflow],
        activities=[ingest_crm_module_activity],
    )

    await worker.run()
# --8<-- [end:on_demand_worker_bootstrap]


# --8<-- [start:on_demand_start]
async def trigger_ingestion(module: str, checkpoint: dict[str, Any] | None = None) -> str:
    temporal_client = await Client.connect("localhost:7233")
    handle = await temporal_client.start_workflow(
        OnDemandCRMIngestionWorkflow.run,
        OnDemandRequest(module=module, checkpoint=checkpoint),
        id=f"zoho-on-demand-{module}",
        task_queue="zoho-on-demand",
    )
    return handle.id
# --8<-- [end:on_demand_start]
