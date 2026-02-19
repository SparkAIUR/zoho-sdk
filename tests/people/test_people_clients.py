from __future__ import annotations

from typing import Any

from zoho.people.client import PeopleClient
from zoho.people.models import PeopleResponse


class DummyPeopleRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"response": {"result": [{"id": "p1", "name": "Person One"}]}}


async def test_people_forms_and_employees_paths() -> None:
    request = DummyPeopleRequest()
    people = PeopleClient(request=request)

    forms = await people.forms.list_forms()
    await people.forms.list_records(form_link_name="employee")
    await people.forms.create_record(form_link_name="employee", data={"Name": "A"})
    await people.employees.list(limit=100)
    await people.files.list(limit=25)

    assert isinstance(forms, PeopleResponse)
    assert forms.result_rows

    paths = [call["path"] for call in request.calls]
    assert "/forms" in paths
    assert "/forms/employee/records" in paths
    assert "/employees" in paths
    assert "/files" in paths
