"""Render MkDocs-authored docs into Sparkify-compatible MDX output."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import yaml

SNIPPET_LINE_RE = re.compile(r'^\s*--8<--\s+"([^"]+)"\s*$')
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")

DOCS_JSON_SCHEMA = "https://mintlify.com/schema/docs.json"

DEFAULT_FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1v7z"/>
  <path d="M9 12l2 2 4-4"/>
</svg>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs"),
        help="Source docs directory containing MkDocs markdown pages.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".sparkify/docs"),
        help="Output directory for Sparkify-ready docs.",
    )
    parser.add_argument(
        "--mkdocs-config",
        type=Path,
        default=Path("mkdocs.yml"),
        help="Path to mkdocs.yml used as navigation source.",
    )
    return parser.parse_args()


def _is_marker_line(line: str, *, marker_name: str, is_start: bool) -> bool:
    marker_type = "start" if is_start else "end"
    return f"[{marker_type}:{marker_name}]" in line and "--8<--" in line


def _detect_language(path: Path) -> str:
    suffix = path.suffix.lower()
    mapping = {
        ".py": "python",
        ".ts": "ts",
        ".tsx": "tsx",
        ".js": "js",
        ".jsx": "jsx",
        ".json": "json",
        ".sh": "bash",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".md": "markdown",
    }
    return mapping.get(suffix, "")


def extract_marked_snippet(source_path: Path, marker_name: str) -> str:
    lines = source_path.read_text(encoding="utf-8").splitlines()

    start_idx: int | None = None
    end_idx: int | None = None
    for idx, line in enumerate(lines):
        if start_idx is None and _is_marker_line(line, marker_name=marker_name, is_start=True):
            start_idx = idx + 1
            continue
        if start_idx is not None and _is_marker_line(line, marker_name=marker_name, is_start=False):
            end_idx = idx
            break

    if start_idx is None or end_idx is None or end_idx < start_idx:
        raise ValueError(f"Snippet marker {marker_name!r} not found in {source_path}")

    return "\n".join(lines[start_idx:end_idx]).rstrip() + "\n"


def _load_snippet_text(directive_value: str, *, repo_root: Path) -> tuple[str, str]:
    if ":" in directive_value:
        source_rel, marker_name = directive_value.rsplit(":", 1)
    else:
        source_rel, marker_name = directive_value, None

    source_path = (repo_root / source_rel).resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Snippet source not found: {source_rel}")

    if marker_name:
        snippet = extract_marked_snippet(source_path, marker_name)
    else:
        snippet = source_path.read_text(encoding="utf-8")

    language = _detect_language(source_path)
    return language, snippet.rstrip() + "\n"


def render_snippet_directive(
    directive_value: str, *, repo_root: Path, fenced: bool
) -> str:
    language, snippet = _load_snippet_text(directive_value, repo_root=repo_root)
    if not fenced:
        return snippet

    if language:
        return f"```{language}\n{snippet.rstrip()}\n```\n"
    return f"```\n{snippet.rstrip()}\n```\n"


def expand_snippets(content: str, *, repo_root: Path) -> str:
    rendered_lines: list[str] = []
    inside_code_fence = False

    for line in content.splitlines():
        if line.strip().startswith("```"):
            inside_code_fence = not inside_code_fence
            rendered_lines.append(line)
            continue

        match = SNIPPET_LINE_RE.match(line)
        if not match:
            rendered_lines.append(line)
            continue

        rendered_lines.extend(
            render_snippet_directive(
                match.group(1),
                repo_root=repo_root,
                fenced=not inside_code_fence,
            )
            .rstrip("\n")
            .splitlines()
        )

    return "\n".join(rendered_lines).rstrip() + "\n"


def normalize_break_tags(content: str) -> str:
    return content.replace("<br>", "<br />")


def page_ref_from_markdown(markdown_relative: Path) -> str:
    relative = markdown_relative.as_posix()
    if relative.endswith(".md"):
        return relative[:-3]
    return relative


def route_from_markdown(markdown_relative: Path) -> str:
    page_ref = page_ref_from_markdown(markdown_relative)
    if page_ref == "index":
        return "/"
    if page_ref.endswith("/index"):
        return f"/{page_ref[:-6]}"
    return f"/{page_ref}"


def rewrite_internal_links(
    *,
    content: str,
    source_relative: Path,
    docs_root: Path,
) -> str:
    current_dir = source_relative.parent

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()
        parsed = urlparse(target)
        if parsed.scheme or parsed.netloc or target.startswith("#"):
            return match.group(0)

        if not parsed.path.endswith(".md"):
            return match.group(0)

        if parsed.path.startswith("/"):
            normalized = posixpath.normpath(parsed.path.lstrip("/"))
        else:
            normalized = posixpath.normpath(posixpath.join(current_dir.as_posix(), parsed.path))

        if normalized.startswith("../") or normalized == "..":
            return match.group(0)

        resolved_relative = Path(normalized)
        if not (docs_root / resolved_relative).is_file():
            return match.group(0)

        new_path = route_from_markdown(resolved_relative)
        rewritten = parsed._replace(path=new_path)
        new_target = urlunparse(rewritten)
        return f"[{label}]({new_target})"

    return MARKDOWN_LINK_RE.sub(replace, content)


def _collect_page_paths(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]

    if isinstance(value, list):
        pages: list[str] = []
        for item in value:
            pages.extend(_collect_page_paths(item))
        return pages

    if isinstance(value, dict):
        pages: list[str] = []
        for nested in value.values():
            pages.extend(_collect_page_paths(nested))
        return pages

    raise ValueError(f"Unsupported mkdocs nav entry type: {type(value)!r}")


def build_navigation_from_mkdocs(nav_items: list[object]) -> list[dict[str, object]]:
    leading_pages: list[str] = []
    trailing_pages: list[str] = []
    section_groups: list[dict[str, object]] = []
    seen_section = False

    for entry in nav_items:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ValueError("Each mkdocs nav entry must be a one-key mapping.")

        group_name, value = next(iter(entry.items()))
        if isinstance(value, str):
            if seen_section:
                trailing_pages.append(value)
            else:
                leading_pages.append(value)
            continue

        if isinstance(value, list):
            seen_section = True
            pages = [page_ref_from_markdown(Path(path)) for path in _collect_page_paths(value)]
            section_groups.append({"group": str(group_name), "pages": pages})
            continue

        raise ValueError(f"Unsupported value for nav entry {group_name!r}: {type(value)!r}")

    navigation: list[dict[str, object]] = []
    if leading_pages:
        navigation.append(
            {
                "group": "Getting Started",
                "pages": [page_ref_from_markdown(Path(path)) for path in leading_pages],
            }
        )

    navigation.extend(section_groups)

    if trailing_pages:
        navigation.append(
            {
                "group": "Reference",
                "pages": [page_ref_from_markdown(Path(path)) for path in trailing_pages],
            }
        )

    return navigation


def render_docs(*, source_dir: Path, output_dir: Path, mkdocs_config_path: Path) -> None:
    source_dir = source_dir.resolve()
    output_dir = output_dir.resolve()
    mkdocs_config_path = mkdocs_config_path.resolve()
    repo_root = mkdocs_config_path.parent

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source docs directory not found: {source_dir}")
    if not mkdocs_config_path.is_file():
        raise FileNotFoundError(f"mkdocs config not found: {mkdocs_config_path}")

    mkdocs_config = yaml.safe_load(mkdocs_config_path.read_text(encoding="utf-8"))
    if not isinstance(mkdocs_config, dict):
        raise ValueError(f"Invalid mkdocs config format in {mkdocs_config_path}")

    raw_nav = mkdocs_config.get("nav")
    if not isinstance(raw_nav, list):
        raise ValueError("mkdocs.yml must include a top-level 'nav' list.")

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for source_file in sorted(source_dir.rglob("*")):
        if not source_file.is_file():
            continue
        relative = source_file.relative_to(source_dir)
        destination = output_dir / relative

        if source_file.suffix.lower() == ".md":
            content = source_file.read_text(encoding="utf-8")
            content = expand_snippets(content, repo_root=repo_root)
            content = rewrite_internal_links(
                content=content,
                source_relative=relative,
                docs_root=source_dir,
            )
            content = normalize_break_tags(content)

            destination = destination.with_suffix(".mdx")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content.rstrip() + "\n", encoding="utf-8")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)

    favicon_path = output_dir / "favicon.svg"
    if not favicon_path.exists():
        source_favicon = source_dir / "favicon.svg"
        if source_favicon.is_file():
            shutil.copy2(source_favicon, favicon_path)
        else:
            favicon_path.write_text(DEFAULT_FAVICON_SVG, encoding="utf-8")

    site_name = str(mkdocs_config.get("site_name") or source_dir.parent.name)
    docs_json = {
        "$schema": DOCS_JSON_SCHEMA,
        "theme": "mint",
        "name": site_name,
        "navigation": build_navigation_from_mkdocs(raw_nav),
    }

    docs_json_path = output_dir / "docs.json"
    docs_json_path.write_text(f"{json.dumps(docs_json, indent=2)}\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    render_docs(
        source_dir=args.source,
        output_dir=args.output,
        mkdocs_config_path=args.mkdocs_config,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
