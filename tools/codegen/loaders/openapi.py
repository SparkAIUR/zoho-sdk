"""Load endpoint definitions from OpenAPI specs."""

from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.ir import EndpointDef

_HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def load_endpoints(path: Path) -> list[EndpointDef]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("openapi spec must be a JSON object")

    paths = data.get("paths")
    if not isinstance(paths, dict):
        return []

    endpoints: list[EndpointDef] = []

    for route in sorted(paths):
        route_item = paths[route]
        if not isinstance(route_item, dict):
            continue

        for method in sorted(route_item):
            if method not in _HTTP_METHODS:
                continue

            operation = route_item[method]
            if not isinstance(operation, dict):
                continue

            operation_id = operation.get("operationId")
            if not isinstance(operation_id, str) or not operation_id:
                operation_id = f"{method}_{route.strip('/').replace('/', '_').replace('{', '').replace('}', '')}"

            tags = operation.get("tags")
            group = (
                tags[0]
                if isinstance(tags, list) and tags and isinstance(tags[0], str)
                else route.strip("/").split("/")[0]
            )
            if not group:
                group = "default"

            endpoints.append(
                EndpointDef(
                    id=f"{group}.{operation_id}",
                    method=method.upper(),
                    path=route,
                    operation_id=operation_id,
                    group=group,
                )
            )

    return endpoints
