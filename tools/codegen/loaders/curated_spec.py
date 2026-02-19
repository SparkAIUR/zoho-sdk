"""Load curated product spec snapshots."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from tools.codegen.ir import EndpointDef


def load_curated_endpoints(spec_paths: Sequence[Path]) -> list[EndpointDef]:
    """Load endpoints from curated JSON spec snapshots."""

    endpoints: list[EndpointDef] = []

    for spec_path in spec_paths:
        payload = json.loads(spec_path.read_text())
        if not isinstance(payload, dict):
            raise ValueError(f"Spec {spec_path} must be a JSON object")

        product = payload.get("product")
        if not isinstance(product, str) or not product:
            raise ValueError(f"Spec {spec_path} is missing product")

        raw_endpoints = payload.get("endpoints")
        if not isinstance(raw_endpoints, list):
            raise ValueError(f"Spec {spec_path} endpoints must be a list")

        for item in raw_endpoints:
            if not isinstance(item, dict):
                continue
            endpoint_id = item.get("id")
            method = item.get("method")
            path = item.get("path")
            operation_id = item.get("operation_id")
            group = item.get("group")
            if not all(
                isinstance(v, str) and v for v in (endpoint_id, method, path, operation_id, group)
            ):
                continue
            endpoints.append(
                EndpointDef(
                    id=endpoint_id,
                    method=method.upper(),
                    path=path,
                    operation_id=operation_id,
                    group=group,
                )
            )

    endpoints.sort(key=lambda item: (item.id, item.method, item.path))
    return endpoints
