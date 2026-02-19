"""People employee APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.people.models import PeopleResponse, parse_people_response

if TYPE_CHECKING:
    from zoho.people.client import PeopleClient


class PeopleEmployeesClient:
    """Employee directory operations for Zoho People."""

    def __init__(self, people_client: PeopleClient) -> None:
        self._people = people_client

    async def list(
        self,
        *,
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
            "/employees",
            params=params,
            headers=headers,
        )
        return parse_people_response(payload)

    async def get(
        self,
        *,
        employee_id: str | int,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "GET",
            f"/employees/{employee_id}",
            headers=headers,
        )
        return parse_people_response(payload)

    async def create(
        self,
        *,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "POST",
            "/employees",
            json={"data": dict(data)},
            headers=headers,
        )
        return parse_people_response(payload)

    async def update(
        self,
        *,
        employee_id: str | int,
        data: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "PUT",
            f"/employees/{employee_id}",
            json={"data": dict(data)},
            headers=headers,
        )
        return parse_people_response(payload)
