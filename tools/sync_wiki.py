"""Sync repository docs into the GitHub wiki.

This script renders docs from `docs/` into wiki-friendly markdown pages:
- flattens page names for GitHub wiki
- expands mkdocs `--8<--` snippet directives
- rewrites internal markdown links to wiki page names
- generates `_Sidebar.md`

Usage:
    uv run python tools/sync_wiki.py --repo SparkAIUR/zoho-sdk --push
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Sequence
from pathlib import Path
from urllib.parse import urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
MKDOCS_CONFIG = REPO_ROOT / "mkdocs.yml"

SNIPPET_LINE_RE = re.compile(r'^\s*--8<--\s+"([^"]+)"\s*$')
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")


def _is_marker_line(line: str, *, marker_name: str, is_start: bool) -> bool:
    marker_type = "start" if is_start else "end"
    return f"[{marker_type}:{marker_name}]" in line and "--8<--" in line


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/name form")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional render-only output dir. If set, clone/push is skipped unless --push is set.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Clone wiki repo, write rendered pages, and push commit.",
    )
    parser.add_argument(
        "--author-name",
        default="zoho-sdk-bot",
        help="Git author name for wiki commit.",
    )
    parser.add_argument(
        "--author-email",
        default="noreply@users.noreply.github.com",
        help="Git author email for wiki commit.",
    )
    parser.add_argument(
        "--commit-message",
        default="docs: sync wiki from docs/",
        help="Commit message used when pushing wiki updates.",
    )
    return parser.parse_args()


def _load_nav_entries() -> list[tuple[str, str]]:
    config = yaml.safe_load(MKDOCS_CONFIG.read_text(encoding="utf-8"))
    nav = config.get("nav", [])
    entries: list[tuple[str, str]] = []

    def walk(items: Sequence[object]) -> None:
        for item in items:
            if isinstance(item, dict):
                for label, value in item.items():
                    if isinstance(value, str):
                        if value.endswith(".md"):
                            entries.append((str(label), value))
                    elif isinstance(value, list):
                        walk(value)
                    else:
                        raise ValueError(
                            f"Unsupported nav entry type for {label!r}: {type(value)!r}"
                        )
            else:
                raise ValueError(f"Unsupported nav item type: {type(item)!r}")

    walk(nav)
    return entries


def _wiki_page_name(doc_rel: str) -> str:
    if doc_rel == "index.md":
        return "Home.md"
    slug = doc_rel[:-3].replace("/", "-")
    return f"{slug}.md"


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


def _extract_marked_snippet(source_path: Path, marker_name: str) -> str:
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


def _load_snippet_text(directive_value: str) -> tuple[str, str]:
    if ":" in directive_value:
        source_rel, marker_name = directive_value.rsplit(":", 1)
    else:
        source_rel, marker_name = directive_value, None

    source_path = (REPO_ROOT / source_rel).resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Snippet source not found: {source_rel}")

    if marker_name:
        snippet = _extract_marked_snippet(source_path, marker_name)
    else:
        snippet = source_path.read_text(encoding="utf-8")

    language = _detect_language(source_path)
    return language, snippet.rstrip() + "\n"


def _render_snippet_directive(directive_value: str, *, fenced: bool) -> str:
    language, snippet = _load_snippet_text(directive_value)
    if not fenced:
        return snippet
    return f"```{language}\n{snippet.rstrip()}\n```\n"


def _expand_snippets(content: str) -> str:
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
            _render_snippet_directive(match.group(1), fenced=not inside_code_fence)
            .rstrip("\n")
            .splitlines()
        )
    return "\n".join(rendered_lines).rstrip() + "\n"


def _rewrite_internal_links(
    *,
    content: str,
    doc_rel: str,
    doc_to_wiki_page: dict[str, str],
) -> str:
    current_dir = Path(doc_rel).parent

    def replace(match: re.Match[str]) -> str:
        label = match.group(1)
        target = match.group(2).strip()
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#"):
            return match.group(0)

        base = target
        anchor = ""
        if "#" in target:
            base, anchor = target.split("#", 1)
            anchor = f"#{anchor}"
        if not base.endswith(".md"):
            return match.group(0)

        normalized = (current_dir / base).as_posix()
        normalized = str(Path(normalized))
        if normalized.startswith("../"):
            return match.group(0)
        if normalized not in doc_to_wiki_page:
            return match.group(0)

        wiki_page = doc_to_wiki_page[normalized].removesuffix(".md")
        return f"[{label}]({wiki_page}{anchor})"

    return MARKDOWN_LINK_RE.sub(replace, content)


def _render_pages(nav_entries: Sequence[tuple[str, str]]) -> tuple[dict[str, str], dict[str, str]]:
    doc_to_wiki_page = {doc_rel: _wiki_page_name(doc_rel) for _, doc_rel in nav_entries}
    pages: dict[str, str] = {}

    for _, doc_rel in nav_entries:
        source = DOCS_ROOT / doc_rel
        raw = source.read_text(encoding="utf-8")
        expanded = _expand_snippets(raw)
        linked = _rewrite_internal_links(
            content=expanded,
            doc_rel=doc_rel,
            doc_to_wiki_page=doc_to_wiki_page,
        )
        pages[doc_to_wiki_page[doc_rel]] = linked
    return doc_to_wiki_page, pages


def _build_sidebar(
    *,
    nav: Sequence[object],
    doc_to_wiki_page: dict[str, str],
) -> str:
    lines: list[str] = ["## Documentation", ""]

    def walk(items: Sequence[object], level: int) -> None:
        indent = "  " * level
        for item in items:
            if not isinstance(item, dict):
                continue
            for label, value in item.items():
                if isinstance(value, str) and value.endswith(".md"):
                    target = doc_to_wiki_page[value].removesuffix(".md")
                    lines.append(f"{indent}- [{label}]({target})")
                elif isinstance(value, list):
                    lines.append(f"{indent}- **{label}**")
                    walk(value, level + 1)

    walk(nav, 0)
    lines.append("")
    return "\n".join(lines)


def _write_rendered(
    *,
    output_dir: Path,
    pages: dict[str, str],
    sidebar: str,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in pages.items():
        (output_dir / filename).write_text(content, encoding="utf-8")
    (output_dir / "_Sidebar.md").write_text(sidebar, encoding="utf-8")


def _run(
    cmd: Iterable[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=cwd,
        check=check,
        text=True,
        capture_output=True,
    )


def _wiki_remote_url(repo: str) -> str:
    return f"https://github.com/{repo}.wiki.git"


def _clone_wiki_repo(repo: str, dest: Path) -> None:
    _run(["gh", "auth", "setup-git"])
    remote = _wiki_remote_url(repo)
    clone = _run(["git", "clone", remote, str(dest)], check=False)
    if clone.returncode == 0:
        return

    stderr = clone.stderr.lower()
    if "repository not found" in stderr:
        raise RuntimeError(
            f"Wiki backing repo not initialized for {repo}. "
            f"Create the first wiki page at https://github.com/{repo}/wiki and rerun."
        )

    summary = clone.stderr.strip().splitlines()[-1] if clone.stderr.strip() else "unknown git error"
    raise RuntimeError(f"Failed to clone wiki repo: {summary}")


def _copy_into_wiki_repo(*, source_dir: Path, wiki_dir: Path) -> bool:
    for path in wiki_dir.glob("*.md"):
        path.unlink()
    for source in source_dir.glob("*.md"):
        shutil.copy2(source, wiki_dir / source.name)

    status = _run(["git", "status", "--porcelain"], cwd=wiki_dir).stdout.strip()
    return bool(status)


def _commit_and_push(
    *,
    wiki_dir: Path,
    author_name: str,
    author_email: str,
    commit_message: str,
) -> None:
    _run(["git", "config", "user.name", author_name], cwd=wiki_dir)
    _run(["git", "config", "user.email", author_email], cwd=wiki_dir)
    _run(["git", "add", "-A"], cwd=wiki_dir)
    _run(["git", "commit", "-m", commit_message], cwd=wiki_dir)
    _run(["git", "push", "origin", "master"], cwd=wiki_dir)


def main() -> int:
    try:
        args = _parse_args()
        nav_entries = _load_nav_entries()
        doc_to_wiki_page, pages = _render_pages(nav_entries)

        nav = yaml.safe_load(MKDOCS_CONFIG.read_text(encoding="utf-8")).get("nav", [])
        sidebar = _build_sidebar(nav=nav, doc_to_wiki_page=doc_to_wiki_page)

        if args.output_dir:
            render_dir = args.output_dir
            if render_dir.exists():
                shutil.rmtree(render_dir)
            _write_rendered(output_dir=render_dir, pages=pages, sidebar=sidebar)
            print(f"Rendered {len(pages)} wiki pages to {render_dir}")
        else:
            with tempfile.TemporaryDirectory(prefix="zoho-wiki-render-") as tmp_render:
                render_dir = Path(tmp_render)
                _write_rendered(output_dir=render_dir, pages=pages, sidebar=sidebar)
                print(f"Rendered {len(pages)} wiki pages")

        if not args.push:
            return 0

        with tempfile.TemporaryDirectory(prefix="zoho-wiki-clone-") as tmp_wiki:
            wiki_dir = Path(tmp_wiki)
            _clone_wiki_repo(args.repo, wiki_dir)
            changed = _copy_into_wiki_repo(source_dir=render_dir, wiki_dir=wiki_dir)
            if not changed:
                print("Wiki is already up to date.")
                return 0
            _commit_and_push(
                wiki_dir=wiki_dir,
                author_name=args.author_name,
                author_email=args.author_email,
                commit_message=args.commit_message,
            )
            print(f"Pushed wiki update to {args.repo}.wiki.git")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
