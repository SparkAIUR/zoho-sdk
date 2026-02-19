from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.loaders.openapi_creator import load_creator_endpoints


def test_creator_endpoint_summary_matches_golden() -> None:
    endpoints = load_creator_endpoints([Path("tests/fixtures/creator_openapi_minimal.json")])

    payload = {
        "endpoint_count": len(endpoints),
        "group_counts": {},
        "method_counts": {},
    }
    for endpoint in endpoints:
        payload["method_counts"][endpoint.method] = (
            payload["method_counts"].get(endpoint.method, 0) + 1
        )
        payload["group_counts"][endpoint.group] = payload["group_counts"].get(endpoint.group, 0) + 1

    payload["group_counts"] = dict(sorted(payload["group_counts"].items()))
    payload["method_counts"] = dict(sorted(payload["method_counts"].items()))

    expected = json.loads(Path("tests/golden/creator_summary.json").read_text())
    assert payload == expected
