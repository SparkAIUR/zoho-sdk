from __future__ import annotations

from typing import Any

import pytest

from zoho.crm.models import PageInfo, RecordListResponse
from zoho.ingestion.crm import iter_crm_documents, iter_crm_module_documents
from zoho.ingestion.models import IngestionCheckpoint
from zoho.ingestion.people import iter_people_form_documents
from zoho.ingestion.sheet import iter_sheet_worksheet_documents
from zoho.ingestion.workdrive import iter_workdrive_recent_documents
from zoho.people.models import PeopleResponse
from zoho.sheet.models import SheetResponse
from zoho.workdrive.models import WorkDriveResponse


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


class _FakeZoho:
    people = _FakePeople()
    sheet = _FakeSheet()
    workdrive = _FakeWorkDrive()
    crm = _FakeCRM()

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
