"""Shared ingestion helpers."""

from __future__ import annotations

from zoho.client import Zoho


def resolve_connection(client: Zoho, connection_name: str) -> Zoho:
    """Resolve a target client view by connection name."""

    if connection_name == "default":
        return client
    return client.for_connection(connection_name)
