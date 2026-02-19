from __future__ import annotations

from typing import Any

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


class _FakeZoho:
    people = _FakePeople()
    sheet = _FakeSheet()
    workdrive = _FakeWorkDrive()

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
