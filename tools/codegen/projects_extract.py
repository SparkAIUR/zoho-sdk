"""Extract Projects V3 endpoints from Zoho live docs or a local HTML snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.codegen.loaders.projects_docs_scraper import (
    _PROJECTS_DOCS_URL,
    extract_projects_spec_from_file,
    extract_projects_spec_from_live_docs,
    write_projects_extracted_spec,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="Optional local HTML snapshot to parse")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--all", action="store_true", help="Include full endpoint set, not just MVP"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.html is not None:
        endpoints = extract_projects_spec_from_file(args.html, mvp_only=not args.all)
        source_url = str(args.html)
    else:
        endpoints = extract_projects_spec_from_live_docs(mvp_only=not args.all)
        source_url = _PROJECTS_DOCS_URL

    write_projects_extracted_spec(
        endpoints=endpoints,
        output_path=args.output,
        source_url=source_url,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
