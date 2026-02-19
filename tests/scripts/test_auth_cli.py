from __future__ import annotations

from pathlib import Path

import httpx
import respx

from zoho.scripts.auth_cli import main


def _write_credentials(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "zoho.env"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_exchange_token_redacts_sensitive_response(monkeypatch, tmp_path: Path, capsys) -> None:
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

        exit_code = main(["exchange-token", "--grant-code", "grant_123"])
        output = capsys.readouterr().out

    assert exit_code == 0
    assert _strip(output).find("***REDACTED***") >= 0
    assert "access_token_value" not in output
    assert "refresh_token_value" not in output
    assert route.calls
    request_body = route.calls[0].request.content.decode()
    assert "grant_type=authorization_code" in request_body
    assert "code=grant_123" in request_body


def test_exchange_token_can_show_secrets(monkeypatch, tmp_path: Path, capsys) -> None:
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

        exit_code = main(["exchange-token", "--grant-code", "grant_123", "--show-secrets"])
        output = capsys.readouterr().out

    assert exit_code == 0
    assert "access_token_value" in output


def test_grant_code_template_mode(monkeypatch, tmp_path: Path, capsys) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    exit_code = main(
        [
            "grant-code",
            "--self-client-id",
            "1000",
            "--scopes",
            "ZohoCRM.modules.ALL,ZohoCRM.users.READ",
        ]
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert '"mode": "template"' in output
    assert "curl_template" in output
    assert "ZohoCRM.modules.ALL" in output


def test_grant_code_execute_requires_cookie(monkeypatch, tmp_path: Path, capsys) -> None:
    env_file = _write_credentials(tmp_path, "ZOHO_CLIENT_ID=test_client_id")
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))

    exit_code = main(
        [
            "grant-code",
            "--self-client-id",
            "1000",
            "--scope",
            "ZohoCRM.modules.ALL",
            "--execute",
        ]
    )
    stderr = capsys.readouterr().err

    assert exit_code == 2
    assert "--session-cookie is required" in stderr


def test_grant_code_execute_posts_when_cookie_provided(monkeypatch, tmp_path: Path, capsys) -> None:
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
        exit_code = main(
            [
                "grant-code",
                "--self-client-id",
                "1000",
                "--scope",
                "ZohoCRM.modules.ALL",
                "--execute",
                "--session-cookie",
                "ZD_CSRF_TOKEN=abc;iamcsr=def",
            ]
        )
        output = capsys.readouterr().out

    assert exit_code == 0
    assert route.calls
    assert route.calls[0].request.headers["Cookie"] == "ZD_CSRF_TOKEN=abc;iamcsr=def"
    assert "sensitive_grant_token" not in output
    assert "***REDACTED***" in output


def _strip(value: str) -> str:
    return value.replace("\n", " ")
