from __future__ import annotations

from typing import Any

from zoho.mail.client import MailClient
from zoho.mail.models import MailResponse


class DummyMailRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"status": {"code": 200}, "data": [{"id": "m1", "subject": "Hello"}]}


async def test_mail_accounts_folders_messages_threads_paths() -> None:
    request = DummyMailRequest()
    mail = MailClient(request=request)

    accounts = await mail.accounts.list()
    await mail.folders.list(account_id="123")
    await mail.messages.list(account_id="123", folder_id="456", start=1, limit=20)
    await mail.threads.get(account_id="123", thread_id="789")

    assert isinstance(accounts, MailResponse)
    assert accounts.result_rows

    paths = [call["path"] for call in request.calls]
    assert "/accounts" in paths
    assert "/accounts/123/folders" in paths
    assert "/accounts/123/messages/view" in paths
    assert "/accounts/123/threads/789" in paths

    messages_call = next(
        call for call in request.calls if call["path"] == "/accounts/123/messages/view"
    )
    assert messages_call["params"]["folderId"] == "456"
    assert messages_call["params"]["limit"] == 20
