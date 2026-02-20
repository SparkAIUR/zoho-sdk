from __future__ import annotations

import re

from tools.security_scan import (
    _DEFAULT_BASELINE,
    ScanBaseline,
    SecretFinding,
    findings_to_report,
    fingerprint_finding,
    scan_text_lines,
)


def test_scan_text_lines_detects_github_token() -> None:
    token = "ghp_" + ("a" * 36)
    text = f'token = "{token}"\\n'

    findings = scan_text_lines(text, source="working_tree", path="example.py")

    assert findings
    assert any(finding.rule_id == "github-token" for finding in findings)


def test_scan_text_lines_does_not_flag_placeholder_secret() -> None:
    text = 'client_secret = "..."\nrefresh_token = "placeholder"\n'

    findings = scan_text_lines(text, source="working_tree", path="example.py")

    assert findings == []


def test_fingerprint_is_stable() -> None:
    finding = SecretFinding(
        source="history",
        rule_id="github-token",
        path="src/example.py",
        line=10,
        commit="abc123",
    )

    assert fingerprint_finding(finding) == fingerprint_finding(finding)


def test_findings_to_report_contains_summary() -> None:
    finding = SecretFinding(
        source="working_tree",
        rule_id="aws-access-key-id",
        path="src/example.py",
        line=1,
        commit=None,
    )

    report = findings_to_report(
        findings=[finding],
        baseline_path=_DEFAULT_BASELINE,
        mode="working-tree",
    )

    assert report["summary"]["finding_count"] == 1
    assert report["summary"]["mode"] == "working-tree"
    assert report["findings"][0]["path"] == "src/example.py"


def test_path_regex_baseline_can_ignore_findings() -> None:
    baseline = ScanBaseline(
        ignore_fingerprints=frozenset(),
        ignore_path_regex=(re.compile(r"^tests/fixtures/"),),
    )
    finding = SecretFinding(
        source="working_tree",
        rule_id="google-api-key",
        path="tests/fixtures/sample.txt",
        line=3,
        commit=None,
    )

    assert any(pattern.search(finding.path) for pattern in baseline.ignore_path_regex)
