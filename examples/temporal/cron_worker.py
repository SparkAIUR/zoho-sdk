"""Temporal cron workflow example for periodic Zoho ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

from zoho import Zoho
from zoho.ingestion import iter_workdrive_recent_documents
from zoho.ingestion.models import IngestionCheckpoint


# --8<-- [start:cron_request]
@dataclass(slots=True)
class CronRequest:
    folder_id: str
    connection_name: str = "default"
    checkpoint: dict[str, Any] | None = None


# --8<-- [end:cron_request]


# --8<-- [start:cron_activity]
@activity.defn
async def ingest_workdrive_recent_activity(request: CronRequest) -> dict[str, Any]:
    client = Zoho.from_credentials(
        client_id="${ZOHO_CLIENT_ID}",
        client_secret="${ZOHO_CLIENT_SECRET}",
        refresh_token="${ZOHO_REFRESH_TOKEN}",
    )

    checkpoint = (
        IngestionCheckpoint.model_validate(request.checkpoint) if request.checkpoint else None
    )
    next_checkpoint: IngestionCheckpoint | None = checkpoint
    files_seen = 0

    try:
        async for batch in iter_workdrive_recent_documents(
            client,
            folder_id=request.folder_id,
            connection_name=request.connection_name,
            checkpoint=checkpoint,
            max_pages=2,
        ):
            files_seen += len(batch.documents)
            next_checkpoint = batch.checkpoint

        return {
            "folder_id": request.folder_id,
            "files_seen": files_seen,
            "next_checkpoint": (
                next_checkpoint.model_dump(mode="python") if next_checkpoint else None
            ),
        }
    finally:
        await client.close()


# --8<-- [end:cron_activity]


# --8<-- [start:cron_workflow]
@workflow.defn
class CronWorkDriveWorkflow:
    @workflow.run
    async def run(self, request: CronRequest) -> dict[str, Any]:
        return await workflow.execute_activity(
            ingest_workdrive_recent_activity,
            request,
            start_to_close_timeout=600,
        )


# --8<-- [end:cron_workflow]


# --8<-- [start:cron_worker_bootstrap]
async def run_worker() -> None:
    temporal_client = await Client.connect("localhost:7233")
    worker = Worker(
        temporal_client,
        task_queue="zoho-cron",
        workflows=[CronWorkDriveWorkflow],
        activities=[ingest_workdrive_recent_activity],
    )
    await worker.run()


# --8<-- [end:cron_worker_bootstrap]


# --8<-- [start:cron_schedule]
async def ensure_hourly_schedule(folder_id: str) -> str:
    temporal_client = await Client.connect("localhost:7233")
    handle = await temporal_client.start_workflow(
        CronWorkDriveWorkflow.run,
        CronRequest(folder_id=folder_id),
        id=f"zoho-workdrive-hourly-{folder_id}",
        task_queue="zoho-cron",
        cron_schedule="0 * * * *",
    )
    return handle.id


# --8<-- [end:cron_schedule]
