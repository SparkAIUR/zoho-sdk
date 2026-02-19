"""Extract Projects V3 endpoint definitions from the official API docs HTML."""

from __future__ import annotations

import html
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx

from tools.codegen.ir import EndpointDef

_PROJECTS_DOCS_URL = "https://projects.zoho.com/api-docs"

_ENDPOINT_BLOCK_RE = re.compile(
    r'<div class="posrel notecode-parent"\s+method="(?P<method>[A-Z]+)".*?'
    r'<span class="widget-custom-scroll">(?P<path>/api/v3/portal/[^<]+)</span>.*?'
    r'id="(?P<opid>[^"]+)-api"',
    re.DOTALL,
)


@dataclass(slots=True, frozen=True)
class ProjectsExtractedSpec:
    source_url: str
    endpoint_count: int
    endpoints: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def fetch_projects_docs_html(
    url: str = _PROJECTS_DOCS_URL, *, timeout_seconds: float = 30.0
) -> str:
    """Fetch Zoho Projects API docs page HTML."""

    response = httpx.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def _normalize_path(raw_path: str) -> str:
    path = html.unescape(raw_path).strip()
    path = path.replace('"', "")
    path = path.replace("&#34;", "")
    path = path.rstrip(",")

    def repl(match: re.Match[str]) -> str:
        token = match.group(1).lower()
        return "{" + token + "}"

    path = re.sub(r"\[([A-Z0-9_]+)\]\+?", repl, path)
    return path


def extract_projects_endpoints(html_text: str) -> list[EndpointDef]:
    """Extract endpoint definitions from Projects API docs HTML."""

    endpoints: list[EndpointDef] = []
    seen: set[tuple[str, str, str]] = set()

    for match in _ENDPOINT_BLOCK_RE.finditer(html_text):
        method = match.group("method").upper()
        raw_path = match.group("path")
        opid_raw = match.group("opid")

        path = _normalize_path(raw_path)
        operation_id = opid_raw.replace("-", "_")

        group = operation_id.split("_", 1)[0] if "_" in operation_id else "projects"
        endpoint_key = (method, path, operation_id)
        if endpoint_key in seen:
            continue
        seen.add(endpoint_key)

        endpoints.append(
            EndpointDef(
                id=f"projects.{group}.{operation_id}",
                method=method,
                path=path,
                operation_id=operation_id,
                group=group,
            )
        )

    endpoints.sort(key=lambda item: (item.path, item.method, item.operation_id))
    return endpoints


def select_projects_mvp_endpoints(endpoints: list[EndpointDef]) -> list[EndpointDef]:
    """Select the V3 MVP subset: portals, projects, and tasks."""

    selected: list[EndpointDef] = []
    for endpoint in endpoints:
        path = endpoint.path
        if path == "/api/v3/portal/{portalid}":
            selected.append(endpoint)
            continue
        if path.startswith("/api/v3/portal/{portalid}/projects"):
            if "/issues" in path or "/comments" in path or "/phases" in path:
                continue
            selected.append(endpoint)
            continue

    selected.sort(key=lambda item: (item.path, item.method, item.operation_id))
    return selected


def write_projects_extracted_spec(
    *,
    endpoints: list[EndpointDef],
    output_path: Path,
    source_url: str = _PROJECTS_DOCS_URL,
) -> None:
    """Write extracted endpoint definitions as deterministic JSON."""

    import json

    output_path.parent.mkdir(parents=True, exist_ok=True)
    spec = ProjectsExtractedSpec(
        source_url=source_url,
        endpoint_count=len(endpoints),
        endpoints=[
            {
                "id": endpoint.id,
                "method": endpoint.method,
                "path": endpoint.path,
                "operation_id": endpoint.operation_id,
                "group": endpoint.group,
            }
            for endpoint in endpoints
        ],
    )
    output_path.write_text(json.dumps(spec.to_dict(), indent=2, sort_keys=True) + "\n")


def extract_projects_spec_from_file(
    html_path: Path,
    *,
    mvp_only: bool,
) -> list[EndpointDef]:
    html_text = html_path.read_text()
    endpoints = extract_projects_endpoints(html_text)
    return select_projects_mvp_endpoints(endpoints) if mvp_only else endpoints


def extract_projects_spec_from_live_docs(*, mvp_only: bool) -> list[EndpointDef]:
    html_text = fetch_projects_docs_html()
    endpoints = extract_projects_endpoints(html_text)
    return select_projects_mvp_endpoints(endpoints) if mvp_only else endpoints
