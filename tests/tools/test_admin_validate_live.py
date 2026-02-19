from __future__ import annotations

import os
from pathlib import Path

import pytest

from tools.admin_validate_live import (
    format_non_sensitive_error,
    load_credentials_file_from_env,
    missing_required_env_vars,
)
from zoho.core.errors import ZohoAPIError


def test_load_credentials_file_from_env_requires_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZOHO_CREDENTIALS_FILE", raising=False)

    with pytest.raises(ValueError, match="ZOHO_CREDENTIALS_FILE"):
        load_credentials_file_from_env()


def test_load_credentials_file_from_env_requires_existing_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    missing = tmp_path / "missing.env"
    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(missing))

    with pytest.raises(ValueError, match="missing file"):
        load_credentials_file_from_env()


def test_load_credentials_file_from_env_loads_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_file = tmp_path / "zoho-live.env"
    env_file.write_text(
        "\n".join(
            [
                "ZOHO_CLIENT_ID=test_client_id",
                "ZOHO_CLIENT_SECRET=test_client_secret",
                "ZOHO_REFRESH_TOKEN=test_refresh_token",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("ZOHO_CREDENTIALS_FILE", str(env_file))
    monkeypatch.delenv("ZOHO_CLIENT_ID", raising=False)
    monkeypatch.delenv("ZOHO_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("ZOHO_REFRESH_TOKEN", raising=False)

    loaded = load_credentials_file_from_env()
    assert loaded == env_file
    assert os.environ["ZOHO_CLIENT_ID"] == "test_client_id"
    assert os.environ["ZOHO_CLIENT_SECRET"] == "test_client_secret"
    assert os.environ["ZOHO_REFRESH_TOKEN"] == "test_refresh_token"


def test_missing_required_env_vars_reports_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZOHO_CLIENT_ID", "id")
    monkeypatch.delenv("ZOHO_CLIENT_SECRET", raising=False)
    monkeypatch.setenv("ZOHO_REFRESH_TOKEN", "refresh")

    assert missing_required_env_vars() == ["ZOHO_CLIENT_SECRET"]


def test_format_non_sensitive_error_hides_messages() -> None:
    err = ZohoAPIError(
        "refresh_token leaked in message",
        status_code=401,
        code="INVALID_OAUTHTOKEN",
        request_id="request_123",
    )

    detail = format_non_sensitive_error(err)
    assert detail == "ZohoAPIError status=401 code=INVALID_OAUTHTOKEN request_id=request_123"
    assert "refresh_token" not in detail
