from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.loaders.curated_spec import load_curated_endpoints


def test_curated_summary_matches_golden() -> None:
    endpoints = load_curated_endpoints(
        [
            Path("tests/fixtures/curated/people_v1_curated.json"),
            Path("tests/fixtures/curated/sheet_v2_curated.json"),
            Path("tests/fixtures/curated/workdrive_v1_curated.json"),
        ]
    )

    payload = {
        "endpoint_count": len(endpoints),
        "method_counts": {},
        "group_counts": {},
        "product_counts": {},
    }

    for endpoint in endpoints:
        payload["method_counts"][endpoint.method] = (
            payload["method_counts"].get(endpoint.method, 0) + 1
        )
        payload["group_counts"][endpoint.group] = payload["group_counts"].get(endpoint.group, 0) + 1
        product = endpoint.id.split(".", 1)[0]
        payload["product_counts"][product] = payload["product_counts"].get(product, 0) + 1

    payload["method_counts"] = dict(sorted(payload["method_counts"].items()))
    payload["group_counts"] = dict(sorted(payload["group_counts"].items()))
    payload["product_counts"] = dict(sorted(payload["product_counts"].items()))

    expected = json.loads(Path("tests/golden/curated_summary.json").read_text())
    assert payload == expected
