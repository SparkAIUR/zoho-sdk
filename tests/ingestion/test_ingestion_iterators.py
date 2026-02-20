from __future__ import annotations

from typing import Any

import pytest

from zoho.analytics.models import AnalyticsResponse
from zoho.cliq.models import CliqResponse
from zoho.crm.models import PageInfo, RecordListResponse
from zoho.ingestion.analytics import (
    iter_analytics_view_documents,
    iter_analytics_workspace_documents,
)
from zoho.ingestion.cliq import (
    iter_cliq_channel_documents,
    iter_cliq_chat_documents,
    iter_cliq_thread_documents,
)
from zoho.ingestion.crm import iter_crm_documents, iter_crm_module_documents
from zoho.ingestion.mail import iter_mail_message_documents
from zoho.ingestion.models import IngestionCheckpoint
from zoho.ingestion.people import iter_people_form_documents
from zoho.ingestion.sheet import iter_sheet_worksheet_documents
from zoho.ingestion.workdrive import iter_workdrive_recent_documents
from zoho.ingestion.writer import iter_writer_document_documents
from zoho.mail.models import MailResponse
from zoho.people.models import PeopleResponse
from zoho.sheet.models import SheetResponse
from zoho.workdrive.models import WorkDriveResponse
from zoho.writer.models import WriterResponse


class _FakePeopleForms:
    async def list_records(self, **_: Any) -> PeopleResponse:
        return PeopleResponse(
            response={
                "result": [
                    {"id": "emp_1", "name": "Alex", "modified_time": "2026-02-19T00:00:00Z"},
                    {"id": "emp_2", "name": "Sam", "modified_time": "2026-02-19T00:01:00Z"},
                ]
            }
        )


class _FakePeople:
    forms = _FakePeopleForms()


class _FakeSheetTabular:
    async def fetch_worksheet_records(self, **_: Any) -> SheetResponse:
        return SheetResponse(records=[{"id": "row_1", "title": "First Row"}])


class _FakeSheet:
    tabular = _FakeSheetTabular()


class _FakeChanges:
    async def list_recent(self, **_: Any) -> WorkDriveResponse:
        return WorkDriveResponse(
            data=[
                {
                    "id": "wd_1",
                    "type": "files",
                    "attributes": {"name": "Spec", "modified_time": "2026-02-19T00:00:00Z"},
                }
            ],
            links={"cursor": {"has_next": False}},
        )


class _FakeWorkDrive:
    changes = _FakeChanges()


class _FakeMailMessages:
    async def list(self, **_: Any) -> MailResponse:
        return MailResponse(
            data=[
                {
                    "messageId": "mail_1",
                    "subject": "New Contract",
                    "summary": "Please review the attached contract.",
                    "receivedTime": "2026-02-19T00:20:00Z",
                }
            ]
        )


class _FakeMail:
    messages = _FakeMailMessages()


class _FakeWriterDocuments:
    async def list(self, **_: Any) -> WriterResponse:
        return WriterResponse(
            data=[
                {
                    "id": "doc_1",
                    "title": "SOW Draft",
                    "description": "Statement of Work draft for legal review.",
                    "modified_time": "2026-02-19T00:21:00Z",
                }
            ]
        )


class _FakeWriter:
    documents = _FakeWriterDocuments()


class _FakeCRMRecords:
    def __init__(self) -> None:
        self._rows: dict[str, list[dict[str, Any]]] = {
            "Leads": [
                {"id": "lead_1", "Full_Name": "Alex Lead", "Modified_Time": "2026-02-19T00:00:00Z"},
                {"id": "lead_2", "Full_Name": "Sam Lead", "Modified_Time": "2026-02-19T00:01:00Z"},
                {"id": "lead_3", "Full_Name": "Pat Lead", "Modified_Time": "2026-02-19T00:02:00Z"},
            ],
            "Contacts": [
                {
                    "id": "contact_1",
                    "Full_Name": "Casey Contact",
                    "Modified_Time": "2026-02-19T00:03:00Z",
                },
            ],
        }

    async def list(
        self,
        *,
        module: str,
        page: int = 1,
        per_page: int = 200,
        fields: list[str] | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> RecordListResponse:
        del fields
        del extra_params

        rows = self._rows.get(module, [])
        start = (page - 1) * per_page
        end = start + per_page
        page_rows = rows[start:end]
        has_more = end < len(rows)
        return RecordListResponse(
            data=page_rows,
            info=PageInfo(page=page, per_page=per_page, more_records=has_more),
        )


class _FakeCRM:
    records = _FakeCRMRecords()


class _FakeCliqChannels:
    async def list(self, **kwargs: Any) -> CliqResponse:
        token = kwargs.get("next_token")
        if token is None:
            return CliqResponse(
                data=[{"id": "channel_1", "name": "Engineering", "modified_time": 1700000100000}],
                next_token="channel_next",
            )
        return CliqResponse(data=[{"id": "channel_2", "name": "Product"}], next_token=None)


class _FakeCliqChats:
    async def list(self, **_: Any) -> CliqResponse:
        return CliqResponse(
            data=[{"id": "chat_1", "title": "Incident Room", "modified_time": 1700000200000}],
            next_token=None,
        )


class _FakeCliqMessages:
    async def list(self, *, chat_id: str, **_: Any) -> CliqResponse:
        if chat_id == "chat_1":
            return CliqResponse(
                data=[
                    {
                        "id": "msg_1",
                        "text": "Service recovered",
                        "time": 1700000201000,
                        "thread_id": "thread_1",
                    }
                ]
            )
        return CliqResponse(data=[])


class _FakeCliqThreads:
    async def get_parent_message(self, *, thread_id: str, **_: Any) -> CliqResponse:
        return CliqResponse(
            data={
                "messages": [
                    {
                        "id": f"{thread_id}_parent",
                        "text": "Parent thread message",
                        "time": 1700000202000,
                    }
                ]
            }
        )

    async def list_followers(self, *, thread_id: str, **_: Any) -> CliqResponse:
        return CliqResponse(data={"followers": [{"id": "user_1", "name": "Alex"}]})


class _FakeCliq:
    channels = _FakeCliqChannels()
    chats = _FakeCliqChats()
    messages = _FakeCliqMessages()
    threads = _FakeCliqThreads()


class _FakeAnalyticsMetadata:
    async def list_organizations(self, **_: Any) -> AnalyticsResponse:
        return AnalyticsResponse(data={"orgs": [{"orgId": "org_1", "orgName": "Acme"}]})

    async def list_workspaces(self, **_: Any) -> AnalyticsResponse:
        return AnalyticsResponse(
            data={"workspaces": [{"workspaceId": "ws_1", "workspaceName": "Ops"}]}
        )

    async def list_views(self, *, workspace_id: str, **_: Any) -> AnalyticsResponse:
        assert workspace_id == "ws_1"
        return AnalyticsResponse(data={"views": [{"viewId": "view_1", "viewName": "Tickets"}]})


class _FakeAnalyticsData:
    async def list_rows(
        self,
        *,
        workspace_id: str,
        view_id: str,
        config: dict[str, Any] | None = None,
        **_: Any,
    ) -> AnalyticsResponse:
        assert workspace_id == "ws_1"
        assert view_id == "view_1"
        offset = int((config or {}).get("offset", 0))
        limit = int((config or {}).get("limit", 200))
        if offset >= 2:
            return AnalyticsResponse(data={"rows": []})
        if limit == 1 and offset == 1:
            return AnalyticsResponse(
                data={"rows": [{"id": "row_2", "name": "Ticket B", "modified_time": 2}]}
            )
        return AnalyticsResponse(
            data={"rows": [{"id": "row_1", "name": "Ticket A", "modified_time": 1}]}
        )


class _FakeAnalyticsBulk:
    def __init__(self) -> None:
        self._poll_calls = 0

    async def export_data(self, **_: Any) -> AnalyticsResponse:
        return AnalyticsResponse(data={"job_id": "job_1"})

    async def get_export_job(self, **_: Any) -> AnalyticsResponse:
        self._poll_calls += 1
        if self._poll_calls == 1:
            return AnalyticsResponse(data={"status": "processing"})
        return AnalyticsResponse(data={"status": "success"})

    async def download_export_job(self, **_: Any) -> AnalyticsResponse:
        return AnalyticsResponse(data={"rows": [{"id": "bulk_1", "name": "Bulk Row"}]})


class _FakeAnalytics:
    metadata = _FakeAnalyticsMetadata()
    data = _FakeAnalyticsData()
    bulk = _FakeAnalyticsBulk()


class _FakeZoho:
    people = _FakePeople()
    sheet = _FakeSheet()
    workdrive = _FakeWorkDrive()
    mail = _FakeMail()
    writer = _FakeWriter()
    crm = _FakeCRM()
    cliq = _FakeCliq()
    analytics = _FakeAnalytics()

    def for_connection(self, name: str) -> _FakeZoho:
        assert name == "tenant"
        return self


async def test_people_ingestion_iterator_yields_checkpoint() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_people_form_documents(
            client,
            form_link_name="employee",
            page_size=200,
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.people"
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.offset == 2


async def test_sheet_ingestion_iterator_uses_connection_name() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_sheet_worksheet_documents(
            client,
            workbook_id="wb1",
            worksheet_name="Sheet1",
            connection_name="tenant",
            checkpoint=IngestionCheckpoint(offset=0),
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.sheet"


async def test_workdrive_ingestion_iterator_yields_documents() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_workdrive_recent_documents(
            client,
            folder_id="folder_1",
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.workdrive"
    assert batches[0].documents[0].id == "wd_1"


async def test_crm_module_ingestion_iterator_paginates() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_crm_module_documents(
            client,
            module="Leads",
            page_size=2,
        )
    ]

    assert len(batches) == 2
    assert batches[0].documents[0].source == "zoho.crm"
    assert batches[0].documents[0].id == "lead_1"
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.page == 2
    assert batches[0].checkpoint.extras["module"] == "Leads"
    assert batches[1].checkpoint is None


async def test_crm_multi_module_ingestion_adds_module_checkpoint_context() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_crm_documents(
            client,
            modules=["Leads", "Contacts"],
            page_size=2,
            max_pages_per_module=1,
        )
    ]

    assert len(batches) == 2
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.extras["module_name"] == "Leads"
    assert batches[0].checkpoint.extras["module_index"] == 0
    assert batches[1].checkpoint is None


async def test_crm_multi_module_ingestion_requires_modules() -> None:
    client = _FakeZoho()

    with pytest.raises(ValueError, match="at least one"):
        async for _ in iter_crm_documents(client, modules=[]):
            pass


async def test_mail_ingestion_iterator_yields_checkpoint() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_mail_message_documents(
            client,
            account_id="account_1",
            folder_id="folder_1",
            page_size=50,
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.mail"
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.offset == 2


async def test_writer_ingestion_iterator_yields_documents() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_writer_document_documents(
            client,
            page_size=100,
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.writer"
    assert batches[0].documents[0].id == "doc_1"


async def test_cliq_channel_ingestion_iterator_yields_checkpoint() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_cliq_channel_documents(
            client,
            page_size=100,
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.cliq.channel"
    assert batches[0].documents[0].content is None
    assert batches[0].documents[0].raw == {}
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.cursor == "channel_next"


async def test_cliq_chat_ingestion_iterator_yields_messages() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_cliq_chat_documents(
            client,
            include_messages=True,
            max_pages=1,
        )
    ]

    assert len(batches) == 1
    sources = {doc.source for doc in batches[0].documents}
    assert "zoho.cliq.chat" in sources
    assert "zoho.cliq.message" in sources
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.updated_at is not None


async def test_cliq_thread_ingestion_iterator_uses_chat_messages() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_cliq_thread_documents(
            client,
            chat_id="chat_1",
            max_threads=1,
        )
    ]

    assert len(batches) == 1
    sources = {doc.source for doc in batches[0].documents}
    assert "zoho.cliq.thread" in sources
    assert "zoho.cliq.thread_follower" in sources


async def test_analytics_workspace_ingestion_iterator_yields_metadata() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_analytics_workspace_documents(
            client,
            include_views=True,
            max_workspaces=1,
        )
    ]

    assert len(batches) == 2
    assert batches[0].documents[0].source == "zoho.analytics.org"
    assert batches[1].documents[0].source == "zoho.analytics.workspace"
    assert any(doc.source == "zoho.analytics.view" for doc in batches[1].documents)


async def test_analytics_view_ingestion_direct_strategy_paginates() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_analytics_view_documents(
            client,
            workspace_id="ws_1",
            view_id="view_1",
            strategy="direct",
            page_size=1,
            max_pages=2,
        )
    ]

    assert len(batches) == 2
    assert batches[0].documents[0].source == "zoho.analytics.row"
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.offset == 1


async def test_analytics_view_ingestion_bulk_strategy_polls_and_downloads() -> None:
    client = _FakeZoho()

    batches = [
        batch
        async for batch in iter_analytics_view_documents(
            client,
            workspace_id="ws_1",
            view_id="view_1",
            strategy="bulk",
            max_poll_attempts=3,
            poll_interval_seconds=0,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents[0].source == "zoho.analytics.row"
    assert batches[0].checkpoint is None


async def test_analytics_view_ingestion_bulk_strategy_returns_job_checkpoint_when_pending() -> None:
    client = _FakeZoho()
    checkpoint = IngestionCheckpoint(cursor="job_pending")

    class _PendingBulk(_FakeAnalyticsBulk):
        async def get_export_job(self, **_: Any) -> AnalyticsResponse:
            return AnalyticsResponse(data={"status": "processing"})

    client.analytics.bulk = _PendingBulk()

    batches = [
        batch
        async for batch in iter_analytics_view_documents(
            client,
            workspace_id="ws_1",
            view_id="view_1",
            strategy="bulk",
            checkpoint=checkpoint,
            max_poll_attempts=1,
            poll_interval_seconds=0,
        )
    ]

    assert len(batches) == 1
    assert batches[0].documents == []
    assert batches[0].checkpoint is not None
    assert batches[0].checkpoint.cursor == "job_pending"
