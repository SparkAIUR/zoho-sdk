"""Ingestion iterator helpers for Zoho Cliq."""

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from datetime import datetime
from typing import Any

from zoho.client import Zoho
from zoho.ingestion._common import resolve_connection
from zoho.ingestion.models import IngestionBatch, IngestionCheckpoint, IngestionDocument


def _to_epoch_millis(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        try:
            normalized = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            return int(dt.timestamp() * 1000)
        except ValueError:
            return None
    return None


def _extract_updated_at(row: Mapping[str, Any]) -> str | None:
    for key in (
        "modified_time",
        "modifiedTime",
        "created_time",
        "createdTime",
        "time",
        "timestamp",
    ):
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str) and value:
            return value
        if isinstance(value, (int, float)):
            return str(int(value))
    return None


def _extract_high_watermark(row: Mapping[str, Any]) -> int | None:
    for key in (
        "modified_time",
        "modifiedTime",
        "created_time",
        "createdTime",
        "time",
        "timestamp",
    ):
        parsed = _to_epoch_millis(row.get(key))
        if parsed is not None:
            return parsed
    return None


def _extract_text(row: Mapping[str, Any]) -> str | None:
    for key in ("text", "content", "message", "description", "summary"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _extract_id(row: Mapping[str, Any], *, fallback: str) -> str:
    for key in ("id", "message_id", "messageId", "chat_id", "chatId", "thread_id", "threadId"):
        value = row.get(key)
        if value is None:
            continue
        return str(value)
    return fallback


async def iter_cliq_channel_documents(
    client: Zoho,
    *,
    name: str | None = None,
    status: str | None = None,
    level: str | None = None,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
    include_content: bool = False,
    include_raw: bool = False,
    headers: Mapping[str, str] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield normalized channel batches from Zoho Cliq."""

    target = resolve_connection(client, connection_name)
    next_token = checkpoint.cursor if checkpoint else None

    pages = 0
    while True:
        response = await target.cliq.channels.list(
            name=name,
            status=status,
            level=level,
            limit=page_size,
            next_token=next_token,
            headers=headers,
        )
        rows = response.result_rows
        if not rows:
            break

        docs: list[IngestionDocument] = []
        high_watermark = _to_epoch_millis(checkpoint.updated_at) if checkpoint else None
        for index, row in enumerate(rows):
            channel_id = _extract_id(row, fallback=f"channel:{pages}:{index}")
            doc = IngestionDocument(
                id=channel_id,
                source="zoho.cliq.channel",
                title=str(row.get("name") or row.get("display_name") or channel_id),
                content=_extract_text(row) if include_content else None,
                updated_at=_extract_updated_at(row),
                metadata={"entity": "channel", "status": status, "level": level},
                raw=dict(row) if include_raw else {},
            )
            docs.append(doc)
            row_watermark = _extract_high_watermark(row)
            if row_watermark is not None and (
                high_watermark is None or row_watermark > high_watermark
            ):
                high_watermark = row_watermark

        next_token = response.next_token
        yield IngestionBatch(
            source="zoho.cliq.channel",
            documents=docs,
            checkpoint=(
                IngestionCheckpoint(
                    cursor=next_token,
                    updated_at=str(high_watermark) if high_watermark is not None else None,
                    extras={
                        "entity": "channel",
                        "name": name,
                        "status": status,
                        "level": level,
                    },
                )
                if next_token is not None
                else None
            ),
        )

        pages += 1
        if max_pages is not None and pages >= max_pages:
            break
        if next_token is None:
            break


async def iter_cliq_chat_documents(
    client: Zoho,
    *,
    connection_name: str = "default",
    page_size: int = 200,
    checkpoint: IngestionCheckpoint | None = None,
    max_pages: int | None = None,
    include_messages: bool = True,
    message_limit: int = 200,
    include_content: bool = False,
    include_raw: bool = False,
    headers: Mapping[str, str] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield chat and optional message documents from Zoho Cliq."""

    target = resolve_connection(client, connection_name)

    next_token = checkpoint.cursor if checkpoint else None
    modified_after = _to_epoch_millis(checkpoint.updated_at) if checkpoint else None
    high_watermark = modified_after

    pages = 0
    while True:
        chat_response = await target.cliq.chats.list(
            limit=page_size,
            next_token=next_token,
            modified_after=modified_after,
            headers=headers,
        )
        chat_rows = chat_response.result_rows
        if not chat_rows:
            break

        docs: list[IngestionDocument] = []
        for chat_index, chat_row in enumerate(chat_rows):
            chat_id = _extract_id(chat_row, fallback=f"chat:{pages}:{chat_index}")
            docs.append(
                IngestionDocument(
                    id=chat_id,
                    source="zoho.cliq.chat",
                    title=str(chat_row.get("title") or chat_row.get("name") or chat_id),
                    content=_extract_text(chat_row) if include_content else None,
                    updated_at=_extract_updated_at(chat_row),
                    metadata={"entity": "chat"},
                    raw=dict(chat_row) if include_raw else {},
                )
            )
            row_watermark = _extract_high_watermark(chat_row)
            if row_watermark is not None and (
                high_watermark is None or row_watermark > high_watermark
            ):
                high_watermark = row_watermark

            if not include_messages:
                continue

            message_response = await target.cliq.messages.list(
                chat_id=chat_id,
                from_time=modified_after,
                limit=message_limit,
                headers=headers,
            )
            for message_index, message_row in enumerate(message_response.result_rows):
                message_id = _extract_id(
                    message_row,
                    fallback=f"{chat_id}:message:{pages}:{message_index}",
                )
                docs.append(
                    IngestionDocument(
                        id=message_id,
                        source="zoho.cliq.message",
                        title=str(
                            message_row.get("sender_name")
                            or message_row.get("user_name")
                            or message_row.get("title")
                            or message_id
                        ),
                        content=_extract_text(message_row) if include_content else None,
                        updated_at=_extract_updated_at(message_row),
                        metadata={
                            "entity": "message",
                            "chat_id": chat_id,
                            "thread_id": (
                                str(message_row.get("thread_id") or message_row.get("threadId"))
                                if message_row.get("thread_id") or message_row.get("threadId")
                                else None
                            ),
                        },
                        raw=dict(message_row) if include_raw else {},
                    )
                )
                row_watermark = _extract_high_watermark(message_row)
                if row_watermark is not None and (
                    high_watermark is None or row_watermark > high_watermark
                ):
                    high_watermark = row_watermark

        next_token = chat_response.next_token
        yield IngestionBatch(
            source="zoho.cliq.chat",
            documents=docs,
            checkpoint=IngestionCheckpoint(
                cursor=next_token,
                updated_at=str(high_watermark) if high_watermark is not None else None,
                extras={
                    "entity": "chat",
                    "include_messages": include_messages,
                    "message_limit": message_limit,
                },
            ),
        )

        pages += 1
        if max_pages is not None and pages >= max_pages:
            break
        if next_token is None:
            break


def _collect_thread_ids(
    *,
    rows: Sequence[Mapping[str, Any]],
    explicit_thread_ids: Sequence[str] | None,
) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()

    def add(value: Any) -> None:
        if value is None:
            return
        normalized = str(value)
        if normalized in seen:
            return
        seen.add(normalized)
        output.append(normalized)

    if explicit_thread_ids:
        for thread_id in explicit_thread_ids:
            add(thread_id)

    for row in rows:
        add(row.get("thread_id") or row.get("threadId") or row.get("thread"))

    return output


async def iter_cliq_thread_documents(
    client: Zoho,
    *,
    chat_id: str | None = None,
    thread_ids: Sequence[str] | None = None,
    connection_name: str = "default",
    checkpoint: IngestionCheckpoint | None = None,
    max_threads: int | None = None,
    include_parent_message: bool = True,
    include_followers: bool = True,
    follower_limit: int = 200,
    include_content: bool = False,
    include_raw: bool = False,
    headers: Mapping[str, str] | None = None,
) -> AsyncIterator[IngestionBatch]:
    """Yield thread metadata documents from Zoho Cliq."""

    if chat_id is None and not thread_ids:
        raise ValueError("chat_id or thread_ids is required for thread ingestion")

    target = resolve_connection(client, connection_name)
    high_watermark = _to_epoch_millis(checkpoint.updated_at) if checkpoint else None

    candidate_rows: list[dict[str, Any]] = []
    if chat_id is not None:
        message_response = await target.cliq.messages.list(
            chat_id=chat_id,
            limit=500,
            headers=headers,
        )
        candidate_rows = [dict(row) for row in message_response.result_rows]

    all_thread_ids = _collect_thread_ids(rows=candidate_rows, explicit_thread_ids=thread_ids)
    start_index = checkpoint.offset if checkpoint and checkpoint.offset is not None else 0

    for processed, index in enumerate(range(start_index, len(all_thread_ids)), start=1):
        thread_id = all_thread_ids[index]
        docs: list[IngestionDocument] = []

        if include_parent_message:
            parent_response = await target.cliq.threads.get_parent_message(
                thread_id=thread_id,
                headers=headers,
            )
            parent_rows = parent_response.result_rows
            for parent_index, parent_row in enumerate(parent_rows):
                parent_id = _extract_id(
                    parent_row,
                    fallback=f"{thread_id}:parent:{parent_index}",
                )
                docs.append(
                    IngestionDocument(
                        id=parent_id,
                        source="zoho.cliq.thread",
                        title=str(
                            parent_row.get("title") or parent_row.get("sender_name") or parent_id
                        ),
                        content=_extract_text(parent_row) if include_content else None,
                        updated_at=_extract_updated_at(parent_row),
                        metadata={
                            "entity": "thread_parent",
                            "thread_id": thread_id,
                            "chat_id": chat_id,
                        },
                        raw=dict(parent_row) if include_raw else {},
                    )
                )
                row_watermark = _extract_high_watermark(parent_row)
                if row_watermark is not None and (
                    high_watermark is None or row_watermark > high_watermark
                ):
                    high_watermark = row_watermark

        if include_followers:
            follower_response = await target.cliq.threads.list_followers(
                thread_id=thread_id,
                limit=follower_limit,
                headers=headers,
            )
            follower_rows = follower_response.result_rows
            for follower_index, follower_row in enumerate(follower_rows):
                follower_id = _extract_id(
                    follower_row,
                    fallback=f"{thread_id}:follower:{follower_index}",
                )
                docs.append(
                    IngestionDocument(
                        id=f"{thread_id}:{follower_id}",
                        source="zoho.cliq.thread_follower",
                        title=str(
                            follower_row.get("name")
                            or follower_row.get("display_name")
                            or follower_id
                        ),
                        content=None,
                        updated_at=None,
                        metadata={
                            "entity": "thread_follower",
                            "thread_id": thread_id,
                            "chat_id": chat_id,
                        },
                        raw=dict(follower_row) if include_raw else {},
                    )
                )

        next_offset = index + 1
        yield IngestionBatch(
            source="zoho.cliq.thread",
            documents=docs,
            checkpoint=(
                IngestionCheckpoint(
                    offset=next_offset,
                    updated_at=str(high_watermark) if high_watermark is not None else None,
                    extras={"entity": "thread", "chat_id": chat_id, "thread_id": thread_id},
                )
                if next_offset < len(all_thread_ids)
                else None
            ),
        )

        if max_threads is not None and processed >= max_threads:
            break
