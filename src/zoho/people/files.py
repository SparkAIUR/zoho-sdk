"""People files APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from zoho.people.models import PeopleResponse, parse_people_response

if TYPE_CHECKING:
    from zoho.people.client import PeopleClient


class PeopleFilesClient:
    """Files operations exposed by Zoho People."""

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
            "/files",
            params=params,
            headers=headers,
        )
        return parse_people_response(payload)

    async def get(
        self,
        *,
        file_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "GET",
            f"/files/{file_id}",
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
            "/files",
            json=dict(data),
            headers=headers,
        )
        return parse_people_response(payload)

    async def delete(
        self,
        *,
        file_id: str,
        headers: Mapping[str, str] | None = None,
    ) -> PeopleResponse:
        payload = await self._people.request(
            "DELETE",
            f"/files/{file_id}",
            headers=headers,
        )
        return parse_people_response(payload)
