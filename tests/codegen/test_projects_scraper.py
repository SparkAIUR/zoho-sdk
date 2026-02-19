from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.loaders.projects_docs_scraper import (
    extract_projects_endpoints,
    select_projects_mvp_endpoints,
)


def test_projects_scraper_mvp_matches_golden() -> None:
    html_text = Path("tests/fixtures/projects/api_docs_sample.html").read_text()
    endpoints = extract_projects_endpoints(html_text)
    mvp = select_projects_mvp_endpoints(endpoints)

    payload = {
        "endpoint_count": len(mvp),
        "source_url": "tests/fixtures/projects/api_docs_sample.html",
        "endpoints": [
            {
                "id": endpoint.id,
                "method": endpoint.method,
                "path": endpoint.path,
                "operation_id": endpoint.operation_id,
                "group": endpoint.group,
            }
            for endpoint in mvp
        ],
    }

    expected = json.loads(Path("tests/golden/projects_extracted_mvp.json").read_text())
    assert payload == expected
