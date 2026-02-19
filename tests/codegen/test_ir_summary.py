from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.main import build_summary


def test_ir_summary_matches_golden() -> None:
    fixtures = Path("tests/fixtures")
    summary = build_summary(
        json_details_path=fixtures / "json_details_minimal.json",
        openapi_path=fixtures / "openapi_minimal.json",
    )

    expected = json.loads(Path("tests/golden/ir_summary.json").read_text())
    assert summary.to_dict() == expected
