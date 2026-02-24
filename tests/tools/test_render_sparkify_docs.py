from __future__ import annotations

import json
from pathlib import Path

from tools.render_sparkify_docs import render_docs


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_render_docs_expands_section_snippets_rewrites_links_and_normalizes_html(tmp_path: Path) -> None:
    repo_root = tmp_path
    source_dir = repo_root / "docs"
    output_dir = repo_root / ".sparkify" / "docs"
    mkdocs_config = repo_root / "mkdocs.yml"

    _write(
        repo_root / "examples" / "demo.py",
        "\n".join(
            [
                "# --8<-- [start:runner]",
                'print("hello from snippet")',
                "# --8<-- [end:runner]",
                "",
            ]
        ),
    )
    _write(
        source_dir / "index.md",
        "\n".join(
            [
                "# Home",
                "",
                '--8<-- "examples/demo.py:runner"',
                "",
                "Need scope details? [Open scopes](scopes.md#catalog).",
                "",
                "line<br>",
                "",
            ]
        ),
    )
    _write(source_dir / "scopes.md", "# Scopes\n")
    mkdocs_config.write_text(
        "\n".join(
            [
                "site_name: Test SDK",
                "nav:",
                "  - Home: index.md",
                "  - Guides:",
                "      - Scopes: scopes.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    render_docs(source_dir=source_dir, output_dir=output_dir, mkdocs_config_path=mkdocs_config)

    index_output = (output_dir / "index.mdx").read_text(encoding="utf-8")
    docs_json = json.loads((output_dir / "docs.json").read_text(encoding="utf-8"))

    assert "```python" in index_output
    assert 'print("hello from snippet")' in index_output
    assert "[Open scopes](/scopes#catalog)" in index_output
    assert "line<br />" in index_output
    assert docs_json["navigation"] == [
        {"group": "Getting Started", "pages": ["index"]},
        {"group": "Guides", "pages": ["scopes"]},
    ]


def test_render_docs_supports_full_file_snippets_and_preserves_assets(tmp_path: Path) -> None:
    repo_root = tmp_path
    source_dir = repo_root / "docs"
    output_dir = repo_root / ".sparkify" / "docs"
    mkdocs_config = repo_root / "mkdocs.yml"

    _write(repo_root / "examples" / "demo.sh", "echo 'full-file snippet'\n")
    _write(source_dir / "index.md", "# Home\n")
    _write(source_dir / "guide.md", '--8<-- "examples/demo.sh"\n')
    _write(source_dir / "section" / "page.md", "# Section Page\n")
    _write(source_dir / "changelog.md", "# Changelog\n")
    _write(source_dir / "stylesheets" / "enterprise.css", "body { color: #123456; }\n")
    _write(source_dir / "favicon.svg", "<svg>custom-favicon</svg>\n")
    mkdocs_config.write_text(
        "\n".join(
            [
                "site_name: Test SDK",
                "nav:",
                "  - Home: index.md",
                "  - Guide: guide.md",
                "  - Section:",
                "      - Section Page: section/page.md",
                "  - Changelog: changelog.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    render_docs(source_dir=source_dir, output_dir=output_dir, mkdocs_config_path=mkdocs_config)

    guide_output = (output_dir / "guide.mdx").read_text(encoding="utf-8")
    docs_json = json.loads((output_dir / "docs.json").read_text(encoding="utf-8"))

    assert "```bash" in guide_output
    assert "echo 'full-file snippet'" in guide_output
    assert (output_dir / "stylesheets" / "enterprise.css").read_text(encoding="utf-8") == "body { color: #123456; }\n"
    assert (output_dir / "favicon.svg").read_text(encoding="utf-8") == "<svg>custom-favicon</svg>\n"
    assert (output_dir / "index.mdx").is_file()
    assert (output_dir / "section" / "page.mdx").is_file()
    assert docs_json["navigation"] == [
        {"group": "Getting Started", "pages": ["index", "guide"]},
        {"group": "Section", "pages": ["section/page"]},
        {"group": "Reference", "pages": ["changelog"]},
    ]


def test_render_docs_writes_favicon_when_source_is_missing(tmp_path: Path) -> None:
    repo_root = tmp_path
    source_dir = repo_root / "docs"
    output_dir = repo_root / ".sparkify" / "docs"
    mkdocs_config = repo_root / "mkdocs.yml"

    _write(source_dir / "index.md", "# Home\n")
    mkdocs_config.write_text(
        "\n".join(
            [
                "site_name: Test SDK",
                "nav:",
                "  - Home: index.md",
                "",
            ]
        ),
        encoding="utf-8",
    )

    render_docs(source_dir=source_dir, output_dir=output_dir, mkdocs_config_path=mkdocs_config)

    favicon = output_dir / "favicon.svg"
    assert favicon.is_file()
    assert "<svg" in favicon.read_text(encoding="utf-8")
