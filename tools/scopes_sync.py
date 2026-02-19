"""Generate OAuth scope catalog docs from curated scope metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import BaseModel, Field


class ProductScopes(BaseModel):
    product: str = Field(min_length=1)
    service_name: str = Field(min_length=1)
    scope_syntax: str = Field(min_length=1)
    operations: list[str] = Field(default_factory=list)
    official_docs: list[str] = Field(default_factory=list)
    common_scopes: list[str] = Field(default_factory=list)
    recommended_read_bundle: list[str] = Field(default_factory=list)
    recommended_write_bundle: list[str] = Field(default_factory=list)
    notes: str | None = None


class ScopeCatalog(BaseModel):
    schema_version: int = Field(ge=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    products: list[ProductScopes] = Field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("tools/specs/scopes_catalog.json"),
        help="Path to the scope catalog source JSON.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/scopes.md"),
        help="Path to write generated markdown docs.",
    )
    return parser.parse_args()


def _join_inline(values: list[str]) -> str:
    return "<br>".join(values) if values else "-"


def _linkify(urls: list[str]) -> str:
    if not urls:
        return "-"
    return "<br>".join(f"[link]({url})" for url in urls)


def render_markdown(catalog: ScopeCatalog) -> str:
    lines: list[str] = [
        f"# {catalog.title}",
        "",
        catalog.description,
        "",
        "Generated from `tools/specs/scopes_catalog.json`.",
        "",
        "## Product Scope Summary",
        "",
        "| Product | Scope Syntax | Read Bundle | Write Bundle | Docs |",
        "|---|---|---|---|---|",
    ]

    for product in catalog.products:
        lines.append(
            "| "
            + " | ".join(
                [
                    product.product,
                    f"`{product.scope_syntax}`",
                    _join_inline([f"`{scope}`" for scope in product.recommended_read_bundle]),
                    _join_inline([f"`{scope}`" for scope in product.recommended_write_bundle]),
                    _linkify(product.official_docs),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Product Details",
            "",
        ]
    )

    for product in catalog.products:
        lines.extend(
            [
                f"### {product.product}",
                "",
                f"- Service prefix: `{product.service_name}`",
                f"- Scope syntax: `{product.scope_syntax}`",
                f"- Supported operations: `{', '.join(product.operations) if product.operations else '-'}`",
                "",
                "Common scope examples:",
                "",
                "| Scope |",
                "|---|",
            ]
        )
        for scope in product.common_scopes:
            lines.append(f"| `{scope}` |")

        if product.notes:
            lines.extend(
                [
                    "",
                    f"Notes: {product.notes}",
                ]
            )

        lines.extend(
            [
                "",
                "References:",
            ]
        )
        for url in product.official_docs:
            lines.append(f"- {url}")
        lines.append("")

    lines.extend(
        [
            "## Regenerate",
            "",
            "```bash",
            "uv run python tools/scopes_sync.py",
            "```",
            "",
            "## Build Scope Sets Interactively",
            "",
            "Use the CLI scope builder when planning app permissions:",
            "",
            "```bash",
            "uv run zoho-auth scope-builder",
            "uv run zoho-auth scope-builder --product CRM --product People --access read --format env",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def load_catalog(path: Path) -> ScopeCatalog:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ScopeCatalog.model_validate(payload)


def main() -> int:
    args = parse_args()
    catalog = load_catalog(args.source)
    markdown = render_markdown(catalog)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
