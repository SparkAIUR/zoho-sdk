"""Creator-specific OpenAPI loader helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from tools.codegen.ir import EndpointDef
from tools.codegen.loaders.openapi import load_endpoints


def load_creator_endpoints(openapi_paths: Sequence[Path]) -> list[EndpointDef]:
    """Load and namespace Creator endpoints from one or more OpenAPI files."""

    endpoints: list[EndpointDef] = []
    for path in openapi_paths:
        for endpoint in load_endpoints(path):
            endpoints.append(
                EndpointDef(
                    id=f"creator.{endpoint.id}",
                    method=endpoint.method,
                    path=endpoint.path,
                    operation_id=endpoint.operation_id,
                    group=endpoint.group,
                )
            )
    return endpoints
