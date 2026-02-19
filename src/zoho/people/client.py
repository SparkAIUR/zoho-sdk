"""Zoho People product client."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from zoho.people.employees import PeopleEmployeesClient
    from zoho.people.files import PeopleFilesClient
    from zoho.people.forms import PeopleFormsClient


class PeopleRequestCallable(Protocol):
    async def __call__(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]: ...


class PeopleClient:
    """Product-scoped People client."""

    def __init__(self, *, request: PeopleRequestCallable) -> None:
        self._request_fn = request
        self._forms: PeopleFormsClient | None = None
        self._employees: PeopleEmployeesClient | None = None
        self._files: PeopleFilesClient | None = None

    @property
    def forms(self) -> PeopleFormsClient:
        if self._forms is None:
            from zoho.people.forms import PeopleFormsClient

            self._forms = PeopleFormsClient(self)
        return self._forms

    @property
    def employees(self) -> PeopleEmployeesClient:
        if self._employees is None:
            from zoho.people.employees import PeopleEmployeesClient

            self._employees = PeopleEmployeesClient(self)
        return self._employees

    @property
    def files(self) -> PeopleFilesClient:
        if self._files is None:
            from zoho.people.files import PeopleFilesClient

            self._files = PeopleFilesClient(self)
        return self._files

    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        return await self._request_fn(
            method,
            path,
            headers=headers,
            params=params,
            json=json,
            data=data,
            files=files,
            timeout=timeout,
        )
