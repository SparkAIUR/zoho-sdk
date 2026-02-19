"""Guards against broken snippet references in MkDocs pages."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
_INCLUDE_PATTERN = re.compile(r'^\s*--8<--\s+"([^"]+)"\s*$')
_START_MARKER_PATTERN = re.compile(r"--8<--\s+\[start:([A-Za-z0-9_.-]+)\]")
_END_MARKER_PATTERN = re.compile(r"--8<--\s+\[end:([A-Za-z0-9_.-]+)\]")


def _iter_include_references() -> list[tuple[Path, str]]:
    references: list[tuple[Path, str]] = []
    for markdown_file in sorted(DOCS_DIR.rglob("*.md")):
        for line in markdown_file.read_text(encoding="utf-8").splitlines():
            match = _INCLUDE_PATTERN.match(line)
            if match:
                references.append((markdown_file, match.group(1)))
    return references


def _resolve_include_path(reference: str) -> tuple[Path, str | None]:
    if ":" in reference:
        raw_path, section = reference.rsplit(":", 1)
    else:
        raw_path, section = reference, None
    return REPO_ROOT / raw_path, section


def test_snippet_include_targets_exist() -> None:
    missing: list[str] = []

    for markdown_file, reference in _iter_include_references():
        include_path, _ = _resolve_include_path(reference)
        if not include_path.exists():
            missing.append(f"{markdown_file}: {reference}")

    assert not missing, "Missing snippet include targets:\n" + "\n".join(missing)


def test_snippet_section_markers_exist() -> None:
    missing_sections: list[str] = []

    for markdown_file, reference in _iter_include_references():
        include_path, section = _resolve_include_path(reference)
        if section is None:
            continue
        content = include_path.read_text(encoding="utf-8")

        start_sections = {match.group(1) for match in _START_MARKER_PATTERN.finditer(content)}
        end_sections = {match.group(1) for match in _END_MARKER_PATTERN.finditer(content)}

        if section not in start_sections or section not in end_sections:
            missing_sections.append(f"{markdown_file}: {reference}")

    assert not missing_sections, "Missing snippet section markers:\n" + "\n".join(missing_sections)
