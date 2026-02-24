from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

import pytest

from zoho.core.cache import AsyncTTLCache
from zoho.crm.client import CRMClient
from zoho.crm.coql import CoqlClient


class DummyCRM:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})

        if method == "POST" and path == "/coql":
            json_payload = kwargs.get("json")
            select_query = (
                json_payload.get("select_query", "") if isinstance(json_payload, dict) else ""
            )
            if (
                "from Deals_X_Contacts" in select_query
                and "Signer_Deals.Loan_ID = 'xxx'" in select_query
            ):
                return {
                    "data": [
                        {
                            "Signers.Email": "signer@example.com",
                            "Signers.Phone": "+1-555-0100",
                        }
                    ],
                    "info": {"count": 1, "more_records": False},
                }
            if select_query.endswith("limit 0, 2"):
                return {
                    "data": [{"id": "1"}, {"id": "2"}],
                    "info": {"count": 2, "more_records": True},
                }
            if select_query.endswith("limit 2, 2"):
                return {
                    "data": [{"id": "3"}],
                    "info": {"count": 1, "more_records": False},
                }

        return {"data": [{"id": "1"}], "info": {"count": 1, "more_records": False}}


def test_crm_client_exposes_lazy_coql_property() -> None:
    async def requester(method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        _ = method
        _ = path
        _ = kwargs
        return {}

    crm = CRMClient(
        request=requester,
        metadata_cache=AsyncTTLCache(),
        default_metadata_ttl_seconds=60,
    )

    first = crm.coql
    second = crm.coql
    assert first is second


async def test_coql_execute_raw_query_with_named_params() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    result = await coql.execute(
        query=(
            "select Signers.Email, Signers.Phone "
            "from Deals_X_Contacts where Signer_Deals.Loan_ID = :loan_id"
        ),
        params={"loan_id": "xxx"},
    )

    assert result.data[0]["Signers.Email"] == "signer@example.com"
    assert result.info is not None
    assert result.info.count == 1

    assert crm.calls[0]["method"] == "POST"
    assert crm.calls[0]["path"] == "/coql"
    assert (
        crm.calls[0]["json"]["select_query"]
        == "select Signers.Email, Signers.Phone from Deals_X_Contacts "
        "where Signer_Deals.Loan_ID = 'xxx'"
    )


async def test_coql_execute_validates_query_shape_and_params() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    with pytest.raises(ValueError, match="must not be empty"):
        await coql.execute(query="  ")

    with pytest.raises(ValueError, match="SELECT and FROM"):
        await coql.execute(query="select id where id is not null")

    with pytest.raises(ValueError, match="loan_id"):
        await coql.execute(query="select id from Deals where Loan_ID = :loan_id")


def test_coql_builder_compiles_and_is_immutable() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    base = coql.select("Last_Name").from_("Leads")
    advanced = base.where_eq("Last_Name", "Ng").order_by("Created_Time desc").limit(10).offset(5)

    assert base.to_query() == "select Last_Name from Leads"
    assert (
        advanced.to_query() == "select Last_Name from Leads where (Last_Name = 'Ng') "
        "order by Created_Time desc limit 5, 10"
    )

    related = (
        coql.select("Signers.Email", "Signers.Phone")
        .from_("Deals_X_Contacts")
        .where("Signer_Deals.Loan_ID = :loan_id", params={"loan_id": "xxx"})
    )
    assert (
        related.to_query() == "select Signers.Email, Signers.Phone from Deals_X_Contacts "
        "where (Signer_Deals.Loan_ID = 'xxx')"
    )


def test_coql_builder_predicates_and_param_conflict_validation() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    query = (
        coql.select("id")
        .from_("Leads")
        .where_eq("Converted", False)
        .where_in("Lead_Source", ["Web", "Chat"])
        .where_eq("Score_Date", date(2026, 2, 24))
        .where_eq("Last_Seen", datetime(2026, 2, 24, 1, 2, 3, tzinfo=UTC))
        .where_is_not_null("Email")
        .to_query()
    )
    assert "Converted = false" in query
    assert "Lead_Source in ('Web', 'Chat')" in query
    assert "Score_Date = '2026-02-24'" in query
    assert "Last_Seen = '2026-02-24T01:02:03+00:00'" in query
    assert "Email is not null" in query

    with pytest.raises(ValueError, match="at least one value"):
        coql.select("id").from_("Leads").where_in("Lead_Source", [])

    with pytest.raises(ValueError, match="Conflicting value"):
        (
            coql.select("id")
            .from_("Leads")
            .where("Loan_ID = :loan_id", params={"loan_id": "x1"})
            .where("Signer_Deals.Loan_ID = :loan_id", params={"loan_id": "x2"})
            .to_query()
        )


async def test_coql_execute_all_paginates_and_merges_rows() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    result = await coql.execute_all(query="select id from Leads", batch_size=2)

    assert [row["id"] for row in result.data] == ["1", "2", "3"]
    assert result.info is not None
    assert result.info.count == 3
    assert result.info.more_records is False

    queries = [call["json"]["select_query"] for call in crm.calls]
    assert queries == [
        "select id from Leads limit 0, 2",
        "select id from Leads limit 2, 2",
    ]


async def test_coql_execute_all_rejects_limit_and_respects_max_records() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    with pytest.raises(ValueError, match="already include LIMIT"):
        await coql.execute_all(query="select id from Leads limit 10")

    result = await coql.execute_all(query="select id from Leads", batch_size=2, max_records=2)
    assert [row["id"] for row in result.data] == ["1", "2"]
    assert len(crm.calls) == 1


async def test_coql_builder_execute_and_execute_all() -> None:
    crm = DummyCRM()
    coql = CoqlClient(crm)

    builder = coql.select("id").from_("Leads").where("id is not null")

    one_page = await builder.execute()
    all_pages = await builder.execute_all(batch_size=2)

    assert one_page.data[0]["id"] == "1"
    assert [row["id"] for row in all_pages.data] == ["1", "2", "3"]
