"""Generate deterministic summary for curated product spec snapshots."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from tools.codegen.loaders.curated_spec import load_curated_endpoints


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    endpoints = load_curated_endpoints(args.spec)

    method_counts = Counter(endpoint.method for endpoint in endpoints)
    group_counts = Counter(endpoint.group for endpoint in endpoints)
    product_counts = Counter(endpoint.id.split(".", 1)[0] for endpoint in endpoints)

    payload = {
        "endpoint_count": len(endpoints),
        "method_counts": dict(sorted(method_counts.items())),
        "group_counts": dict(sorted(group_counts.items())),
        "product_counts": dict(sorted(product_counts.items())),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
