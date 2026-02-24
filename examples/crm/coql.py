"""Reusable COQL usage snippets for CRM workflows."""

from __future__ import annotations

from zoho import Zoho


# --8<-- [start:raw_query]
async def run_raw_coql_query(client: Zoho, *, loan_id: str) -> None:
    response = await client.crm.coql.execute(
        query=(
            "select Signers.Email, Signers.Phone "
            "from Deals_X_Contacts where Signer_Deals.Loan_ID = :loan_id"
        ),
        params={"loan_id": loan_id},
    )
    for row in response.data:
        print(row.get("Signers.Email"), row.get("Signers.Phone"))


# --8<-- [end:raw_query]


# --8<-- [start:builder_query]
async def run_builder_coql_query(client: Zoho, *, loan_id: str) -> None:
    query = (
        client.crm.coql.select("Signers.Email", "Signers.Phone")
        .from_("Deals_X_Contacts")
        .where("Signer_Deals.Loan_ID = :loan_id", params={"loan_id": loan_id})
        .order_by("id asc")
        .limit(200)
    )
    response = await query.execute()
    for row in response.data:
        print(row.get("Signers.Email"), row.get("Signers.Phone"))


# --8<-- [end:builder_query]


# --8<-- [start:execute_all]
async def run_coql_paged_fetch(client: Zoho) -> None:
    response = await client.crm.coql.execute_all(
        query="select id, Last_Name from Leads where Last_Name is not null",
        batch_size=2000,
        max_records=10000,
    )
    print("rows", len(response.data))


# --8<-- [end:execute_all]
