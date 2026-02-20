from __future__ import annotations

import json
import re
from contextlib import suppress
from pathlib import Path

import httpx
import respx
from click.testing import Result
from typer.testing import CliRunner

from zoho.scripts.auth_cli import app

runner = CliRunner()
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _write_credentials(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "zoho.env"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def _normalized_cli_output(result: Result) -> str:
    chunks = [result.stdout, result.stderr]
    with suppress(AttributeError):
        chunks.append(result.output)
    return _ANSI_ESCAPE_RE.sub("", "\n".join(chunk for chunk in chunks if chunk))


def test_exchange_token_redacts_sensitive_response(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(
        tmp_path,
        "\n".join(
            [
                "ZOHO_CLIENT_ID=test_client_id",
                "ZOHO_CLIENT_SECRET=test_client_secret",
                "ZOHO_DC=US",
            ]
        ),
    )
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    with respx.mock(assert_all_called=True) as router:
        route = router.post("https://accounts.zoho.com/oauth/v2/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "access_token_value",
                    "refresh_token": "refresh_token_value",
                    "api_domain": "https://www.zohoapis.com",
                },
            )
        )

        result = runner.invoke(app, ["exchange-token", "--grant-code", "grant_123"])

    assert result.exit_code == 0
    assert "***REDACTED***" in result.stdout
    assert "access_token_value" not in result.stdout
    assert "refresh_token_value" not in result.stdout
    assert route.calls
    request_body = route.calls[0].request.content.decode()
    assert "grant_type=authorization_code" in request_body
    assert "code=grant_123" in request_body


def test_exchange_token_can_show_secrets(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(
        tmp_path,
        "\n".join(
            [
                "ZOHO_CLIENT_ID=test_client_id",
                "ZOHO_CLIENT_SECRET=test_client_secret",
                "ZOHO_DC=US",
            ]
        ),
    )
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    with respx.mock(assert_all_called=True) as router:
        router.post("https://accounts.zoho.com/oauth/v2/token").mock(
            return_value=httpx.Response(
                200,
                json={
                    "access_token": "access_token_value",
                },
            )
        )

        result = runner.invoke(
            app, ["exchange-token", "--grant-code", "grant_123", "--show-secrets"]
        )

    assert result.exit_code == 0
    assert "access_token_value" in result.stdout


def test_grant_code_template_mode(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    result = runner.invoke(
        app,
        [
            "grant-code",
            "--self-client-id",
            "1000",
            "--scopes",
            "ZohoCRM.modules.ALL,ZohoCRM.users.READ",
        ],
    )

    assert result.exit_code == 0
    assert '"mode": "template"' in result.stdout
    assert "curl_template" in result.stdout
    assert "ZohoCRM.modules.ALL" in result.stdout


def test_grant_code_execute_requires_cookie(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    result = runner.invoke(
        app,
        [
            "grant-code",
            "--self-client-id",
            "1000",
            "--scope",
            "ZohoCRM.modules.ALL",
            "--execute",
        ],
    )
    assert result.exit_code == 2
    output = _normalized_cli_output(result)
    assert "--session-cookie is required" in output


def test_grant_code_execute_posts_when_cookie_provided(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    with respx.mock(assert_all_called=True) as router:
        route = router.post(
            "https://api-console.zoho.com/oauthapi/v1/selfclient/1000/granttoken"
        ).mock(
            return_value=httpx.Response(
                201,
                json={
                    "granttoken": {"Grant_token": "sensitive_grant_token"},
                    "message": "Success",
                },
            )
        )
        result = runner.invoke(
            app,
            [
                "grant-code",
                "--self-client-id",
                "1000",
                "--scope",
                "ZohoCRM.modules.ALL",
                "--execute",
                "--session-cookie",
                "ZD_CSRF_TOKEN=abc;iamcsr=def",
            ],
        )

    assert result.exit_code == 0
    assert route.calls
    assert route.calls[0].request.headers["Cookie"] == "ZD_CSRF_TOKEN=abc;iamcsr=def"
    assert "sensitive_grant_token" not in result.stdout
    assert "***REDACTED***" in result.stdout


def test_grant_code_rejects_invalid_scope_token(monkeypatch, tmp_path: Path) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    result = runner.invoke(
        app,
        [
            "grant-code",
            "--self-client-id",
            "1000",
            "--scope",
            "ZohoCRM.modules.{module}.READ",
        ],
    )

    assert result.exit_code == 2
    assert "Invalid scope value(s)" in _normalized_cli_output(result)


def test_scope_builder_non_interactive_json_output() -> None:
    result = runner.invoke(
        app,
        [
            "scope-builder",
            "--product",
            "CRM",
            "--product",
            "People",
            "--access",
            "read",
            "--no-interactive",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["products"] == ["CRM", "People"]
    assert payload["access_profile"] == "read"
    assert "ZohoCRM.modules.READ" in payload["scopes"]
    assert "ZOHOPEOPLE.forms.READ" in payload["scopes"]


def test_scope_builder_interactive_prompts_with_presets() -> None:
    result = runner.invoke(
        app,
        [
            "scope-builder",
            "--product",
            "CRM",
            "--format",
            "env",
        ],
        input="admin\ny\nZohoCRM.apis.READ\n",
    )

    assert result.exit_code == 0
    assert "export ZOHO_SCOPES=" in result.stdout
    assert "ZohoCRM.modules.ALL" in result.stdout
    assert "ZohoCRM.apis.READ" in result.stdout


def test_scope_builder_requires_product_or_interactive() -> None:
    result = runner.invoke(app, ["scope-builder", "--no-interactive", "--access", "read"])

    assert result.exit_code == 2
    output = _normalized_cli_output(result)
    assert "At least one --product is required" in output


def test_scope_builder_rejects_invalid_scope_token() -> None:
    result = runner.invoke(
        app,
        [
            "scope-builder",
            "--product",
            "CRM",
            "--access",
            "read",
            "--scope",
            "Bad{Scope}",
            "--no-interactive",
        ],
    )

    assert result.exit_code == 2
    assert "Invalid scope value(s)" in _normalized_cli_output(result)
