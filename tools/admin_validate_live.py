"""Validate live Zoho credentials using read-only product checks.

This script is intended for administrators validating tenant credentials and
scope coverage before production usage.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv

from zoho import Zoho
from zoho.core.errors import ZohoAPIError
from zoho.core.logging import configure_logging, get_logger

_CREDENTIALS_FILE_ENV_VAR = "ZOHO_CREDENTIALS_FILE"
_REQUIRED_ENV_VARS: tuple[str, ...] = (
    "ZOHO_CLIENT_ID",
    "ZOHO_CLIENT_SECRET",
    "ZOHO_REFRESH_TOKEN",
)


ResultStatus = Literal["ok", "failed", "skipped"]


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Per-check validation status."""

    check: str
    status: ResultStatus
    detail: str


def load_credentials_file_from_env(*, env_var: str = _CREDENTIALS_FILE_ENV_VAR) -> Path:
    """Load `.env` credentials file path from `env_var` and apply with dotenv."""

    raw_path = os.getenv(env_var)
    if not raw_path:
        raise ValueError(f"{env_var} is required and must point to a credentials .env file.")

    credentials_path = Path(raw_path).expanduser()
    if not credentials_path.is_file():
        raise ValueError(f"{env_var} points to a missing file: {credentials_path}")

    load_dotenv(dotenv_path=credentials_path, override=False)
    return credentials_path


def missing_required_env_vars() -> list[str]:
    """Return missing SDK required env vars after dotenv loading."""

    return [name for name in _REQUIRED_ENV_VARS if not os.getenv(name)]


def format_non_sensitive_error(exc: Exception) -> str:
    """Build a safe error summary without response payload leakage."""

    if isinstance(exc, ZohoAPIError):
        parts: list[str] = [exc.__class__.__name__]
        if exc.status_code is not None:
            parts.append(f"status={exc.status_code}")
        if exc.code:
            parts.append(f"code={exc.code}")
        if exc.request_id:
            parts.append(f"request_id={exc.request_id}")
        return " ".join(parts)
    return exc.__class__.__name__


def _count_sheet_workbooks(payload: Any) -> int:
    workbooks = getattr(payload, "workbooks", None)
    if isinstance(workbooks, list):
        return len(workbooks)

    data = getattr(payload, "data", None)
    if isinstance(data, list):
        return len([item for item in data if isinstance(item, dict)])
    if isinstance(data, dict):
        nested = data.get("workbooks")
        if isinstance(nested, list):
            return len([item for item in nested if isinstance(item, dict)])
    return 0


def _count_workdrive_resources(payload: Any) -> int:
    resources = getattr(payload, "resources", None)
    if isinstance(resources, list):
        return len(resources)
    return 0


async def _run_check(
    *,
    check: str,
    call: Callable[[], Awaitable[Any]],
    summarize: Callable[[Any], str],
) -> ValidationResult:
    try:
        value = await call()
    except Exception as exc:  # pragma: no cover - exercised in live execution
        return ValidationResult(
            check=check, status="failed", detail=format_non_sensitive_error(exc)
        )

    try:
        detail = summarize(value)
    except Exception:  # pragma: no cover - defensive only
        detail = "read_ok"
    return ValidationResult(check=check, status="ok", detail=detail)


async def run_read_only_validation(client: Zoho) -> list[ValidationResult]:
    """Run GET-only checks across supported products."""

    results: list[ValidationResult] = []

    results.append(
        await _run_check(
            check="crm.org.get",
            call=lambda: client.crm.org.get(),
            summarize=lambda org: f"org_fields={len(org) if isinstance(org, dict) else 0}",
        )
    )
    results.append(
        await _run_check(
            check="crm.modules.list",
            call=lambda: client.crm.modules.list(use_cache=False),
            summarize=lambda modules: f"modules={len(modules) if isinstance(modules, list) else 0}",
        )
    )

    portals: list[Any] = []
    try:
        portals = await client.projects.portals.list()
    except Exception as exc:  # pragma: no cover - exercised in live execution
        results.append(
            ValidationResult(
                check="projects.portals.list",
                status="failed",
                detail=format_non_sensitive_error(exc),
            )
        )
    else:
        results.append(
            ValidationResult(
                check="projects.portals.list",
                status="ok",
                detail=f"portals={len(portals)}",
            )
        )

    portal_id = os.getenv("ZOHO_PROJECTS_PORTAL_ID")
    if portal_id is None and portals:
        portal_id = portals[0].id

    if portal_id:
        results.append(
            await _run_check(
                check="projects.projects.list",
                call=lambda: client.projects.projects.list(portal_id=portal_id, per_page=1),
                summarize=lambda projects: (
                    f"projects_sample={len(projects) if isinstance(projects, list) else 0}"
                ),
            )
        )
    else:
        results.append(
            ValidationResult(
                check="projects.projects.list",
                status="skipped",
                detail="set ZOHO_PROJECTS_PORTAL_ID or ensure portal access",
            )
        )

    creator_owner = os.getenv("ZOHO_CREATOR_ACCOUNT_OWNER")
    creator_app = os.getenv("ZOHO_CREATOR_APP_LINK_NAME")
    if creator_owner and creator_app:
        results.append(
            await _run_check(
                check="creator.meta.get_forms",
                call=lambda: client.creator.meta.get_forms(
                    account_owner_name=creator_owner,
                    app_link_name=creator_app,
                ),
                summarize=lambda response: f"forms={len(getattr(response, 'data', []))}",
            )
        )
    else:
        results.append(
            ValidationResult(
                check="creator.meta.get_forms",
                status="skipped",
                detail="set ZOHO_CREATOR_ACCOUNT_OWNER and ZOHO_CREATOR_APP_LINK_NAME",
            )
        )

    results.append(
        await _run_check(
            check="people.forms.list_forms",
            call=lambda: client.people.forms.list_forms(),
            summarize=lambda response: f"forms={len(getattr(response, 'result_rows', []))}",
        )
    )
    results.append(
        await _run_check(
            check="sheet.workbooks.list",
            call=lambda: client.sheet.workbooks.list(limit=5),
            summarize=lambda response: f"workbooks_sample={_count_sheet_workbooks(response)}",
        )
    )
    results.append(
        await _run_check(
            check="workdrive.admin.list_teams",
            call=lambda: client.workdrive.admin.list_teams(),
            summarize=lambda response: f"teams={_count_workdrive_resources(response)}",
        )
    )
    results.append(
        await _run_check(
            check="cliq.users.list",
            call=lambda: client.cliq.users.list(limit=5),
            summarize=lambda response: f"users_sample={len(getattr(response, 'result_rows', []))}",
        )
    )
    results.append(
        await _run_check(
            check="analytics.metadata.list_organizations",
            call=lambda: client.analytics.metadata.list_organizations(),
            summarize=lambda response: f"orgs={len(getattr(response, 'result_rows', []))}",
        )
    )
    results.append(
        await _run_check(
            check="writer.documents.list",
            call=lambda: client.writer.documents.list(limit=5),
            summarize=lambda response: (
                f"documents_sample={len(getattr(response, 'result_rows', []))}"
            ),
        )
    )
    results.append(
        await _run_check(
            check="mail.accounts.list",
            call=lambda: client.mail.accounts.list(),
            summarize=lambda response: f"accounts={len(getattr(response, 'result_rows', []))}",
        )
    )

    return results


def _log_result(result: ValidationResult) -> None:
    logger = get_logger("zoho.admin.validate")
    payload = {"check": result.check, "detail": result.detail}
    if result.status == "ok":
        logger.info("validation.check.ok", **payload)
    elif result.status == "skipped":
        logger.warning("validation.check.skipped", **payload)
    else:
        logger.error("validation.check.failed", **payload)


async def _async_main() -> int:
    logger = get_logger("zoho.admin.validate")

    try:
        credentials_path = load_credentials_file_from_env()
    except ValueError as exc:
        logger.error("validation.config_error", detail=str(exc))
        return 2

    missing = missing_required_env_vars()
    if missing:
        logger.error("validation.missing_required_env", missing=missing)
        return 2

    logger.info("validation.start", credentials_file=credentials_path.name)
    client = Zoho.from_env()
    try:
        results = await run_read_only_validation(client)
    finally:
        await client.close()

    success = 0
    failed = 0
    skipped = 0

    for result in results:
        _log_result(result)
        if result.status == "ok":
            success += 1
        elif result.status == "failed":
            failed += 1
        else:
            skipped += 1

    logger.info("validation.summary", success=success, failed=failed, skipped=skipped)
    return 1 if failed else 0


def main() -> int:
    configure_logging(
        log_format=os.getenv("ZOHO_LOG_FORMAT", "pretty"),
        log_level=os.getenv("ZOHO_LOG_LEVEL", "INFO"),
    )
    return asyncio.run(_async_main())


if __name__ == "__main__":
    raise SystemExit(main())
