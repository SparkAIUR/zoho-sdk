from __future__ import annotations

from typing import Any

from zoho.writer.client import WriterClient
from zoho.writer.models import WriterResponse


class DummyWriterRequest:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"status": "success", "data": [{"id": "w1", "name": "Doc 1"}]}


async def test_writer_documents_folders_merge_paths() -> None:
    request = DummyWriterRequest()
    writer = WriterClient(request=request)

    docs = await writer.documents.list(limit=10)
    await writer.folders.create(name="Contracts")
    await writer.merge.get_fields(document_id="doc_1")

    assert isinstance(docs, WriterResponse)
    assert docs.result_rows

    paths = [call["path"] for call in request.calls]
    assert "/documents" in paths
    assert "/folders" in paths
    assert "/documents/doc_1/fields" in paths
