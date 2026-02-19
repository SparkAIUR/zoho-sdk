"""Generate deterministic codegen IR summary for CRM spec inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.codegen.ir import IRSummary
from tools.codegen.loaders.crm_json_details import load_models
from tools.codegen.loaders.openapi import load_endpoints


def build_summary(*, json_details_path: Path, openapi_path: Path) -> IRSummary:
    models, field_count, spec_type_counts = load_models(json_details_path)
    endpoints = load_endpoints(openapi_path)

    interface_count = sum(1 for model in models if model.interface)

    return IRSummary(
        model_count=len(models),
        interface_count=interface_count,
        field_count=field_count,
        endpoint_count=len(endpoints),
        spec_type_counts=dict(sorted(spec_type_counts.items())),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-details", type=Path, required=True)
    parser.add_argument("--openapi", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_summary(json_details_path=args.json_details, openapi_path=args.openapi)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
