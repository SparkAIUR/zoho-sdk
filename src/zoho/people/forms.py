"""People forms and records APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.people.models import PeopleResponse, parse_people_response

if TYPE_CHECKING:
    from zoho.people.client import PeopleClient


class PeopleFormsClient:
    """Forms metadata and record operations for Zoho People."""

    def __init__(self, people_client: PeopleClient) -> None:
        self._people = people_client

    async def list_forms(self, *, headers: Mapping[str, str] | None = None) -> PeopleResponse:
        payload = await self._people.request("GET", "/forms", headers=headers)
        return parse_people_response(payload)

    async def get_fields(
        self,
        *,
        form_link_name: str,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "GET",
            f"/forms/{form_link_name}/fields",
            headers=headers,
        )
        return parse_people_response(payload)

    async def list_records(
        self,
        *,
        form_link_name: str,
        from_index: int | None = None,
        limit: int | None = None,
        extra_params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        params: dict[str, Any] = {}
        if from_index is not None:
            params["from"] = from_index
        if limit is not None:
            params["limit"] = limit
        if extra_params:
            params.update(extra_params)

        payload = await self._people.request(
            "GET",
            f"/forms/{form_link_name}/records",
            params=params,
            headers=headers,
        )
        return parse_people_response(payload)

    async def search_records(
        self,
        *,
        form_link_name: str,
        criteria: str,
        from_index: int | None = None,
        limit: int | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        params: dict[str, Any] = {"criteria": criteria}
        if from_index is not None:
            params["from"] = from_index
        if limit is not None:
            params["limit"] = limit

        payload = await self._people.request(
            "GET",
            f"/forms/{form_link_name}/records/search",
            params=params,
            headers=headers,
        )
        return parse_people_response(payload)

    async def create_record(
        self,
        *,
        form_link_name: str,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "POST",
            f"/forms/{form_link_name}/records",
            json={"data": dict(data)},
            headers=headers,
        )
        return parse_people_response(payload)

    async def update_record(
        self,
        *,
        form_link_name: str,
        record_id: str | int,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "PUT",
            f"/forms/{form_link_name}/records/{record_id}",
            json={"data": dict(data)},
            headers=headers,
        )
        return parse_people_response(payload)
