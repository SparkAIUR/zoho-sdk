"""High-confidence secret scanning for working tree and git history.

This scanner is intentionally conservative: it targets high-signal credential
patterns and reports locations without echoing secret values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_BASELINE = _REPO_ROOT / ".security" / "secrets-baseline.json"
_DEFAULT_REPORT = _REPO_ROOT / ".security" / "secrets-report.json"


@dataclass(frozen=True, slots=True)
class SecretRule:
    """Secret detection rule metadata."""

    rule_id: str
    description: str
    pattern: re.Pattern[str]


@dataclass(frozen=True, slots=True)
class SecretFinding:
    """A single high-confidence secret finding."""

    source: str
    rule_id: str
    path: str
    line: int
    commit: str | None = None


@dataclass(frozen=True, slots=True)
class ScanBaseline:
    """Allow-list data to suppress known-safe findings."""

    ignore_fingerprints: frozenset[str]
    ignore_path_regex: tuple[re.Pattern[str], ...]


_RULES: tuple[SecretRule, ...] = (
    SecretRule(
        rule_id="private-key-header",
        description="Private key material header",
        pattern=re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PRIVATE) PRIVATE KEY-----"),
    ),
    SecretRule(
        rule_id="github-token",
        description="GitHub personal/app token",
        pattern=re.compile(
            r"(?:\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,255}\b|\bgithub_pat_[A-Za-z0-9_]{20,255}\b)"
        ),
    ),
    SecretRule(
        rule_id="aws-access-key-id",
        description="AWS access key identifier",
        pattern=re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    SecretRule(
        rule_id="slack-token",
        description="Slack token",
        pattern=re.compile(r"\bxox(?:b|a|p|r|s)-[A-Za-z0-9-]{10,}\b"),
    ),
    SecretRule(
        rule_id="google-api-key",
        description="Google API key",
        pattern=re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ),
    SecretRule(
        rule_id="zoho-oauth-header",
        description="Zoho OAuth header with long token",
        pattern=re.compile(r"\bZoho-oauthtoken\s+[A-Za-z0-9._-]{20,}\b"),
    ),
    SecretRule(
        rule_id="bearer-token-header",
        description="Bearer header with long token",
        pattern=re.compile(r"\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._=-]{20,}\b", re.IGNORECASE),
    ),
    SecretRule(
        rule_id="long-token-assignment",
        description="Quoted long token/secret assignment",
        pattern=re.compile(
            r"\b(?:client_secret|refresh_token|access_token|api_key)\b\s*[:=]\s*[\"'][A-Za-z0-9._/-]{30,}[\"']",
            re.IGNORECASE,
        ),
    ),
)


def _run_git(args: list[str], *, cwd: Path = _REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def _tracked_files() -> list[Path]:
    result = _run_git(["ls-files", "-z"])
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {result.stderr.strip()}")

    files = [Path(value) for value in result.stdout.split("\0") if value]
    return [path for path in files if (_REPO_ROOT / path).is_file()]


def _parse_baseline(path: Path) -> ScanBaseline:
    if not path.exists():
        return ScanBaseline(ignore_fingerprints=frozenset(), ignore_path_regex=tuple())

    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_fingerprints = payload.get("ignore_fingerprints", [])
    raw_path_regex = payload.get("ignore_path_regex", [])

    fingerprints: set[str] = set()
    for value in raw_fingerprints:
        if isinstance(value, str) and value:
            fingerprints.add(value)

    compiled_paths: list[re.Pattern[str]] = []
    for value in raw_path_regex:
        if isinstance(value, str) and value:
            compiled_paths.append(re.compile(value))

    return ScanBaseline(
        ignore_fingerprints=frozenset(fingerprints),
        ignore_path_regex=tuple(compiled_paths),
    )


def fingerprint_finding(finding: SecretFinding) -> str:
    key = "|".join(
        [
            finding.source,
            finding.rule_id,
            finding.path,
            str(finding.line),
            finding.commit or "",
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def _is_ignored_by_path(path: str, baseline: ScanBaseline) -> bool:
    return any(pattern.search(path) for pattern in baseline.ignore_path_regex)


def _is_allowed(finding: SecretFinding, baseline: ScanBaseline) -> bool:
    if _is_ignored_by_path(finding.path, baseline):
        return True
    return fingerprint_finding(finding) in baseline.ignore_fingerprints


def _matching_rule_ids(line: str) -> list[str]:
    rule_ids: list[str] = []
    for rule in _RULES:
        if rule.pattern.search(line):
            rule_ids.append(rule.rule_id)
    return rule_ids


def scan_text_lines(
    text: str,
    *,
    source: str,
    path: str,
    commit: str | None = None,
) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        rule_ids = _matching_rule_ids(line)
        for rule_id in rule_ids:
            findings.append(
                SecretFinding(
                    source=source,
                    rule_id=rule_id,
                    path=path,
                    line=line_number,
                    commit=commit,
                )
            )
    return findings


def scan_working_tree(*, baseline: ScanBaseline) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    for file_path in _tracked_files():
        relative = file_path.as_posix()
        if _is_ignored_by_path(relative, baseline):
            continue
        try:
            text = (_REPO_ROOT / file_path).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if "\x00" in text:
            continue

        for finding in scan_text_lines(text, source="working_tree", path=relative):
            if not _is_allowed(finding, baseline):
                findings.append(finding)
    return findings


def _commits() -> list[str]:
    result = _run_git(["rev-list", "--all"])
    if result.returncode != 0:
        raise RuntimeError(f"git rev-list failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line]


def scan_history(*, baseline: ScanBaseline) -> list[SecretFinding]:
    findings: list[SecretFinding] = []
    commits = _commits()

    combined_pattern = "|".join(f"(?:{rule.pattern.pattern})" for rule in _RULES)

    for commit in commits:
        result = _run_git(["grep", "-nI", "-P", combined_pattern, commit])
        if result.returncode not in (0, 1):
            raise RuntimeError(f"git grep failed for commit {commit[:12]}: {result.stderr.strip()}")
        if result.returncode == 1:
            continue

        for raw_line in result.stdout.splitlines():
            parts = raw_line.split(":", 3)
            if len(parts) < 4:
                continue
            grep_commit, path, line_text, line_value = parts
            if grep_commit != commit:
                continue
            if _is_ignored_by_path(path, baseline):
                continue

            try:
                line_number = int(line_text)
            except ValueError:
                continue

            for rule_id in _matching_rule_ids(line_value):
                finding = SecretFinding(
                    source="history",
                    rule_id=rule_id,
                    path=path,
                    line=line_number,
                    commit=commit,
                )
                if not _is_allowed(finding, baseline):
                    findings.append(finding)

    return findings


def _finding_payload(finding: SecretFinding) -> dict[str, Any]:
    return {
        "source": finding.source,
        "rule_id": finding.rule_id,
        "path": finding.path,
        "line": finding.line,
        "commit": finding.commit,
        "fingerprint": fingerprint_finding(finding),
    }


def findings_to_report(
    *,
    findings: list[SecretFinding],
    baseline_path: Path,
    mode: str,
) -> dict[str, Any]:
    return {
        "summary": {
            "mode": mode,
            "finding_count": len(findings),
            "rules": sorted({finding.rule_id for finding in findings}),
        },
        "baseline": str(baseline_path),
        "findings": [_finding_payload(finding) for finding in findings],
    }


def _print_findings_text(findings: list[SecretFinding]) -> None:
    if not findings:
        print("No high-confidence secret findings detected.")
        return

    print(f"Detected {len(findings)} high-confidence secret finding(s):")
    for finding in findings:
        commit_suffix = f" @{finding.commit[:12]}" if finding.commit else ""
        print(
            f"- [{finding.source}] {finding.rule_id} {finding.path}:{finding.line}{commit_suffix}"
        )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan tracked files and git history for high-confidence secrets.",
    )
    parser.add_argument(
        "--mode",
        choices=("working-tree", "history", "all"),
        default="all",
        help="Scan mode.",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        default=_DEFAULT_BASELINE,
        help="Path to baseline allow-list JSON file.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=_DEFAULT_REPORT,
        help="Path to write JSON report.",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Always exit 0 even if findings are detected.",
    )
    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    baseline = _parse_baseline(args.baseline)

    findings: list[SecretFinding] = []
    if args.mode in ("working-tree", "all"):
        findings.extend(scan_working_tree(baseline=baseline))
    if args.mode in ("history", "all"):
        findings.extend(scan_history(baseline=baseline))

    report = findings_to_report(
        findings=findings,
        baseline_path=args.baseline,
        mode=args.mode,
    )

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    _print_findings_text(findings)

    if findings and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
