from __future__ import annotations

import json
from pathlib import Path

from tools.scopes_sync import load_catalog, render_markdown


def test_render_markdown_includes_product_summary(tmp_path: Path) -> None:
    source = tmp_path / "scopes.json"
    source.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "title": "Scope Catalog",
                "description": "Test catalog.",
                "products": [
                    {
                        "product": "CRM",
                        "service_name": "ZohoCRM",
                        "scope_syntax": "ZohoCRM.<scope_name>.<operation>",
                        "operations": ["READ", "ALL"],
                        "official_docs": ["https://example.com/crm/scopes"],
                        "common_scopes": ["ZohoCRM.modules.READ"],
                        "recommended_read_bundle": ["ZohoCRM.modules.READ"],
                        "recommended_write_bundle": ["ZohoCRM.modules.ALL"],
                        "notes": "Least privilege.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    catalog = load_catalog(source)
    markdown = render_markdown(catalog)

    assert "# Scope Catalog" in markdown
    assert "| CRM | `ZohoCRM.<scope_name>.<operation>` |" in markdown
    assert "`ZohoCRM.modules.READ`" in markdown
    assert "Least privilege." in markdown
    assert "uv run python tools/scopes_sync.py" in markdown
