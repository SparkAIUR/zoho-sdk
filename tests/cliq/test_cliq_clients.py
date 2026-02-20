from __future__ import annotations

from typing import Any

from zoho.cliq.client import CliqClient
from zoho.cliq.models import CliqResponse


class DummyCliqRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"status": "success", "data": [{"id": "c1", "name": "Item 1"}]}


async def test_cliq_core_paths() -> None:
    request = DummyCliqRequest()
    cliq = CliqClient(request=request)

    channels = await cliq.channels.list(limit=20)
    await cliq.users.list(limit=10)
    await cliq.messages.list(chat_id="chat_1", limit=50)
    await cliq.threads.list_followers(thread_id="thread_1", limit=25)

    assert isinstance(channels, CliqResponse)
    assert channels.result_rows

    paths = [call["path"] for call in request.calls]
    assert "/channels" in paths
    assert "/users" in paths
    assert "/chats/chat_1/messages" in paths
    assert "/threads/thread_1/followers" in paths
