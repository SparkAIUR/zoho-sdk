"""Typer CLI helpers for Zoho OAuth and scope planning workflows."""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any

import click
import httpx
import typer
from dotenv import load_dotenv

app = typer.Typer(
    help="Zoho authentication and scope helper commands.",
    add_completion=False,
    no_args_is_help=True,
)

_ACCOUNTS_DOMAIN_BY_DC: dict[str, str] = {
    "US": "https://accounts.zoho.com",
    "EU": "https://accounts.zoho.eu",
    "IN": "https://accounts.zoho.in",
    "AU": "https://accounts.zoho.com.au",
    "JP": "https://accounts.zoho.jp",
    "CA": "https://accounts.zohocloud.ca",
    "SA": "https://accounts.zoho.sa",
    "CN": "https://accounts.zoho.com.cn",
}

_REDACTED = "***REDACTED***"
_SENSITIVE_KEY_MARKERS = ("token", "secret", "cookie", "authorization", "password")
_SCOPE_TOKEN_PATTERN = re.compile(r"^[0-9a-zA-Z._ ]+$")
_PRODUCT_NAME_BY_ALIAS: dict[str, str] = {
    "crm": "CRM",
    "creator": "Creator",
    "projects": "Projects",
    "people": "People",
    "sheet": "Sheet",
    "workdrive": "WorkDrive",
    "cliq": "Cliq",
    "analytics": "Analytics",
    "writer": "Writer",
    "mail": "Mail",
}


@dataclass(frozen=True, slots=True)
class ScopeSpec:
    read: tuple[str, ...]
    write: tuple[str, ...]
    common: tuple[str, ...]


_SCOPE_CATALOG: dict[str, ScopeSpec] = {
    "CRM": ScopeSpec(
        read=(
            "ZohoCRM.modules.READ",
            "ZohoCRM.settings.READ",
            "ZohoCRM.users.READ",
            "ZohoCRM.org.READ",
        ),
        write=(
            "ZohoCRM.modules.ALL",
            "ZohoCRM.settings.ALL",
            "ZohoCRM.users.READ",
            "ZohoCRM.org.READ",
        ),
        common=(
            "ZohoCRM.modules.READ",
            "ZohoCRM.modules.ALL",
            "ZohoCRM.settings.READ",
            "ZohoCRM.settings.ALL",
            "ZohoCRM.users.READ",
            "ZohoCRM.org.READ",
            "ZohoCRM.coql.READ",
            "ZohoCRM.apis.READ",
        ),
    ),
    "Creator": ScopeSpec(
        read=(
            "ZohoCreator.report.READ",
            "ZohoCreator.meta.form.READ",
            "ZohoCreator.meta.application.READ",
        ),
        write=(
            "ZohoCreator.report.ALL",
            "ZohoCreator.form.CREATE",
            "ZohoCreator.meta.application.READ",
        ),
        common=(
            "ZohoCreator.report.READ",
            "ZohoCreator.report.CREATE",
            "ZohoCreator.report.UPDATE",
            "ZohoCreator.report.DELETE",
            "ZohoCreator.form.CREATE",
            "ZohoCreator.meta.form.READ",
            "ZohoCreator.meta.application.READ",
            "ZohoCreator.dashboard.READ",
        ),
    ),
    "Projects": ScopeSpec(
        read=(
            "ZohoProjects.portals.READ",
            "ZohoProjects.projects.READ",
            "ZohoProjects.tasks.READ",
        ),
        write=(
            "ZohoProjects.projects.ALL",
            "ZohoProjects.tasks.ALL",
            "ZohoProjects.tasklists.ALL",
        ),
        common=(
            "ZohoProjects.portals.READ",
            "ZohoProjects.projects.READ",
            "ZohoProjects.projects.ALL",
            "ZohoProjects.tasklists.READ",
            "ZohoProjects.tasks.READ",
            "ZohoProjects.tasks.UPDATE",
            "ZohoProjects.users.READ",
            "ZohoProjects.search.READ",
            "ZohoPC.files.CREATE",
        ),
    ),
    "People": ScopeSpec(
        read=(
            "ZOHOPEOPLE.forms.READ",
            "ZOHOPEOPLE.employee.ALL",
        ),
        write=(
            "ZOHOPEOPLE.forms.ALL",
            "ZOHOPEOPLE.employee.ALL",
        ),
        common=(
            "ZOHOPEOPLE.forms.READ",
            "ZOHOPEOPLE.forms.ALL",
            "ZOHOPEOPLE.employee.ALL",
            "ZOHOPEOPLE.attendance.ALL",
            "ZOHOPEOPLE.leave.READ",
            "ZOHOPEOPLE.timetracker.ALL",
        ),
    ),
    "Sheet": ScopeSpec(
        read=("ZohoSheet.dataAPI.READ",),
        write=(
            "ZohoSheet.dataAPI.READ",
            "ZohoSheet.dataAPI.UPDATE",
        ),
        common=(
            "ZohoSheet.dataAPI.READ",
            "ZohoSheet.dataAPI.UPDATE",
        ),
    ),
    "WorkDrive": ScopeSpec(
        read=(
            "WorkDrive.team.READ",
            "WorkDrive.files.READ",
        ),
        write=(
            "WorkDrive.team.ALL",
            "WorkDrive.files.ALL",
        ),
        common=(
            "WorkDrive.team.ALL",
            "WorkDrive.files.READ",
            "WorkDrive.files.CREATE",
            "WorkDrive.files.UPDATE",
            "WorkDrive.files.DELETE",
        ),
    ),
    "Cliq": ScopeSpec(
        read=(
            "ZohoCliq.Users.READ",
            "ZohoCliq.Chats.READ",
            "ZohoCliq.Channels.READ",
            "ZohoCliq.Messages.READ",
        ),
        write=(
            "ZohoCliq.Users.UPDATE",
            "ZohoCliq.Channels.UPDATE",
            "ZohoCliq.Messages.UPDATE",
            "ZohoCliq.Webhooks.CREATE",
        ),
        common=(
            "ZohoCliq.Users.READ",
            "ZohoCliq.Users.UPDATE",
            "ZohoCliq.Chats.READ",
            "ZohoCliq.Channels.READ",
            "ZohoCliq.Channels.UPDATE",
            "ZohoCliq.Messages.READ",
            "ZohoCliq.Messages.UPDATE",
            "ZohoCliq.Webhooks.CREATE",
        ),
    ),
    "Analytics": ScopeSpec(
        read=(
            "ZohoAnalytics.metadata.read",
            "ZohoAnalytics.data.read",
        ),
        write=(
            "ZohoAnalytics.metadata.read",
            "ZohoAnalytics.data.create",
            "ZohoAnalytics.data.update",
        ),
        common=(
            "ZohoAnalytics.metadata.read",
            "ZohoAnalytics.data.read",
            "ZohoAnalytics.data.create",
            "ZohoAnalytics.data.update",
            "ZohoAnalytics.data.delete",
            "ZohoAnalytics.usermanagement.read",
        ),
    ),
    "Writer": ScopeSpec(
        read=("ZohoWriter.documentEditor.ALL",),
        write=(
            "ZohoWriter.documentEditor.ALL",
            "ZohoWriter.merge.ALL",
            "ZohoPC.files.ALL",
            "WorkDrive.files.ALL",
        ),
        common=(
            "ZohoWriter.documentEditor.ALL",
            "ZohoWriter.merge.ALL",
            "ZohoPC.files.ALL",
            "WorkDrive.files.ALL",
            "WorkDrive.organization.ALL",
            "WorkDrive.workspace.ALL",
            "ZohoSign.documents.ALL",
        ),
    ),
    "Mail": ScopeSpec(
        read=(
            "ZohoMail.accounts.READ",
            "ZohoMail.folders.READ",
            "ZohoMail.messages.READ",
            "ZohoMail.threads.READ",
        ),
        write=(
            "ZohoMail.accounts.READ",
            "ZohoMail.folders.ALL",
            "ZohoMail.messages.ALL",
            "ZohoMail.threads.ALL",
        ),
        common=(
            "ZohoMail.accounts.READ",
            "ZohoMail.folders.READ",
            "ZohoMail.folders.ALL",
            "ZohoMail.messages.READ",
            "ZohoMail.messages.ALL",
            "ZohoMail.threads.READ",
            "ZohoMail.threads.ALL",
        ),
    ),
}


class AccessProfile(StrEnum):
    read = "read"
    write = "write"
    admin = "admin"


class OutputFormat(StrEnum):
    json = "json"
    text = "text"
    env = "env"


def _print_json(payload: Any) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def _require_credentials_file(path: str | None) -> Path:
    if not path:
        raise typer.BadParameter("ZOHO_CREDENTIALS_FILE is required for this command")
    credentials_path = Path(path).expanduser()
    if not credentials_path.is_file():
        raise typer.BadParameter(f"Credentials file does not exist: {credentials_path}")
    return credentials_path


def _load_credentials_env(credentials_file: str | None) -> Path:
    resolved = _require_credentials_file(credentials_file or os.getenv("ZOHO_CREDENTIALS_FILE"))
    load_dotenv(dotenv_path=resolved, override=False)
    return resolved


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise typer.BadParameter(f"Missing required environment variable: {name}")
    return value


def _sanitize_payload(value: Any, *, show_secrets: bool) -> Any:
    if show_secrets:
        return value

    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_lower = key.lower()
            if any(marker in key_lower for marker in _SENSITIVE_KEY_MARKERS):
                redacted[key] = _REDACTED
            else:
                redacted[key] = _sanitize_payload(item, show_secrets=show_secrets)
        return redacted
    if isinstance(value, list):
        return [_sanitize_payload(item, show_secrets=show_secrets) for item in value]
    return value


def _dedupe(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            deduped.append(value)
    return deduped


def _extract_scopes(*, scopes_csv: str | None, scope_items: list[str] | None) -> list[str]:
    scopes: list[str] = []
    if scopes_csv:
        scopes.extend(scope.strip() for scope in scopes_csv.split(",") if scope.strip())
    if scope_items:
        scopes.extend(scope.strip() for scope in scope_items if scope.strip())
    return _dedupe(scopes)


def _validate_scope_tokens(scopes: list[str]) -> list[str]:
    invalid = [
        scope for scope in scopes if (not scope) or (_SCOPE_TOKEN_PATTERN.fullmatch(scope) is None)
    ]
    if invalid:
        pretty = ", ".join(repr(scope) for scope in invalid)
        raise typer.BadParameter(
            "Invalid scope value(s): "
            + pretty
            + ". Allowed token characters: letters, numbers, dot, underscore, and spaces."
        )
    return scopes


def _resolve_accounts_domain(explicit_domain: str | None) -> str:
    if explicit_domain:
        return explicit_domain.rstrip("/")
    env_domain = os.getenv("ZOHO_ACCOUNTS_DOMAIN")
    if env_domain:
        return env_domain.rstrip("/")
    dc = os.getenv("ZOHO_DC", "US").upper()
    return _ACCOUNTS_DOMAIN_BY_DC.get(dc, _ACCOUNTS_DOMAIN_BY_DC["US"])


def _parse_extra_headers(values: list[str] | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in values or []:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --header format: {item!r}. Expected KEY=VALUE.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise typer.BadParameter(f"Invalid --header format: {item!r}. Header key is empty.")
        headers[key] = value
    return headers


def _http_response_to_json(response: httpx.Response) -> dict[str, Any]:
    try:
        body = response.json()
    except ValueError:
        return {
            "status_code": response.status_code,
            "text": response.text[:500],
        }
    if isinstance(body, dict):
        body.setdefault("status_code", response.status_code)
        return body
    return {
        "status_code": response.status_code,
        "data": body,
    }


def _build_grant_payload(
    *,
    scopes_csv: str | None,
    scope_items: list[str] | None,
    expiry: int,
    description: str,
    approved_orgs: str | None,
) -> dict[str, Any]:
    scopes = _validate_scope_tokens(_extract_scopes(scopes_csv=scopes_csv, scope_items=scope_items))
    if not scopes:
        raise typer.BadParameter("At least one scope is required (--scopes or --scope)")

    grant_payload: dict[str, Any] = {
        "scope": scopes,
        "expiry": expiry,
        "description": description,
    }
    if approved_orgs:
        grant_payload["approvedorgs"] = approved_orgs
    return {"granttoken": grant_payload}


def _grant_endpoint(api_console_domain: str, self_client_id: str) -> str:
    return f"{api_console_domain.rstrip('/')}/oauthapi/v1/selfclient/{self_client_id}/granttoken"


def _render_grant_curl_template(endpoint: str, payload: dict[str, Any]) -> str:
    payload_raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return "\n".join(
        [
            f"curl {shlex.quote(endpoint)} \\",
            "  -H 'Accept: */*' \\",
            "  -H 'Content-Type: application/json' \\",
            "  -H 'Cookie: <SESSION_COOKIE>' \\",
            "  -H 'x-zcsrf-token: <X_ZCSRF_TOKEN>' \\",
            f"  --data-raw {shlex.quote(payload_raw)}",
        ]
    )


def _normalize_product_name(value: str) -> str:
    normalized = value.strip().lower()
    canonical = _PRODUCT_NAME_BY_ALIAS.get(normalized)
    if canonical is None:
        accepted = ", ".join(sorted(_SCOPE_CATALOG))
        raise typer.BadParameter(f"Unknown product {value!r}. Expected one of: {accepted}")
    return canonical


def _select_products(*, preset_products: list[str] | None, interactive: bool) -> list[str]:
    if preset_products:
        return _dedupe([_normalize_product_name(item) for item in preset_products])

    if not interactive:
        raise typer.BadParameter("At least one --product is required when using --no-interactive")

    selected: list[str] = []
    for product in _SCOPE_CATALOG:
        if typer.confirm(f"Include {product} scopes?", default=(product == "CRM")):
            selected.append(product)

    if not selected:
        raise typer.BadParameter("At least one product must be selected")
    return selected


def _resolve_access_profile(*, access: AccessProfile | None, interactive: bool) -> AccessProfile:
    if access is not None:
        return access
    if not interactive:
        raise typer.BadParameter("--access is required when using --no-interactive")

    while True:
        selected = typer.prompt("Access profile [read/write/admin]", default="read").strip().lower()
        try:
            return AccessProfile(selected)
        except ValueError:
            typer.echo("Invalid access profile. Use read, write, or admin.", err=True)


def _resolve_include_common(*, include_common: bool | None, interactive: bool) -> bool:
    if include_common is not None:
        return include_common
    if interactive:
        return typer.confirm(
            "Include common scope examples for each selected product?", default=False
        )
    return False


def _resolve_additional_scopes(
    *,
    additional_scope: list[str] | None,
    interactive: bool,
) -> list[str]:
    extras = _validate_scope_tokens(_extract_scopes(scopes_csv=None, scope_items=additional_scope))
    if extras:
        return extras
    if not interactive:
        return []

    prompted = typer.prompt(
        "Additional scopes (comma-separated, optional)",
        default="",
        show_default=False,
    )
    return _validate_scope_tokens(_extract_scopes(scopes_csv=prompted, scope_items=None))


def _scopes_for_product(
    *,
    product: str,
    access: AccessProfile,
    include_common: bool,
) -> list[str]:
    spec = _SCOPE_CATALOG[product]
    if access is AccessProfile.read:
        scopes = list(spec.read)
    elif access is AccessProfile.write:
        scopes = list(spec.write)
    else:
        scopes = list(spec.write)
        scopes.extend([scope for scope in spec.common if ".ALL" in scope])

    if include_common:
        scopes.extend(spec.common)
    return _dedupe(scopes)


def _render_scope_output(*, payload: dict[str, Any], output_format: OutputFormat) -> str:
    scopes = payload["scopes"]
    scopes_csv = payload["scopes_csv"]

    if output_format is OutputFormat.json:
        return json.dumps(payload, indent=2, sort_keys=True)
    if output_format is OutputFormat.text:
        lines = [
            "Selected products: " + ", ".join(payload["products"]),
            f"Access profile: {payload['access_profile']}",
            f"Scope count: {payload['scope_count']}",
            "Scopes:",
        ]
        lines.extend(f"- {scope}" for scope in scopes)
        lines.extend(["", f"CSV: {scopes_csv}"])
        return "\n".join(lines)

    return "\n".join(
        [
            f'export ZOHO_SCOPES="{scopes_csv}"',
            'echo "$ZOHO_SCOPES"',
            'uv run zoho-auth grant-code --self-client-id <id> --scopes "$ZOHO_SCOPES"',
        ]
    )


@app.command("exchange-token")
def exchange_token(
    grant_code: Annotated[str, typer.Option("--grant-code", help="Authorization grant code.")],
    credentials_file: Annotated[
        str | None,
        typer.Option(
            "--credentials-file",
            help="Optional .env override path. Defaults to ZOHO_CREDENTIALS_FILE.",
        ),
    ] = None,
    accounts_domain: Annotated[
        str | None,
        typer.Option("--accounts-domain", help="Accounts domain override."),
    ] = None,
    redirect_uri: Annotated[
        str | None,
        typer.Option("--redirect-uri", help="Optional redirect URI."),
    ] = None,
    timeout: Annotated[float, typer.Option("--timeout", min=1.0)] = 30.0,
    show_secrets: Annotated[bool, typer.Option("--show-secrets")] = False,
) -> None:
    """Exchange an authorization code for OAuth tokens."""

    _load_credentials_env(credentials_file)
    client_id = _required_env("ZOHO_CLIENT_ID")
    client_secret = _required_env("ZOHO_CLIENT_SECRET")
    resolved_accounts_domain = _resolve_accounts_domain(accounts_domain)

    payload: dict[str, str] = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": grant_code,
    }
    resolved_redirect_uri = redirect_uri or os.getenv("ZOHO_REDIRECT_URI")
    if resolved_redirect_uri:
        payload["redirect_uri"] = resolved_redirect_uri

    token_url = f"{resolved_accounts_domain}/oauth/v2/token"
    with httpx.Client(timeout=timeout) as http:
        response = http.post(
            token_url,
            data=payload,
            headers={"User-Agent": "zoho-auth-cli/0.1.1"},
        )

    body = _http_response_to_json(response)
    safe = _sanitize_payload(body, show_secrets=show_secrets)
    _print_json(safe)
    if response.status_code >= 400:
        raise typer.Exit(code=1)


@app.command("grant-code")
def grant_code(
    self_client_id: Annotated[
        str | None,
        typer.Option("--self-client-id", help="Self-client identifier."),
    ] = None,
    scopes: Annotated[
        str | None,
        typer.Option("--scopes", help="Comma-separated scopes."),
    ] = None,
    scope: Annotated[
        list[str] | None,
        typer.Option("--scope", help="Repeatable scope option."),
    ] = None,
    expiry: Annotated[int, typer.Option("--expiry", min=1)] = 10,
    description: Annotated[str, typer.Option("--description")] = "Evaluation of Zoho SDK",
    approved_orgs: Annotated[str | None, typer.Option("--approved-orgs")] = None,
    api_console_domain: Annotated[
        str,
        typer.Option("--api-console-domain", help="API Console domain."),
    ] = "https://api-console.zoho.com",
    execute: Annotated[bool, typer.Option("--execute")] = False,
    session_cookie: Annotated[
        str | None,
        typer.Option("--session-cookie", help="Session cookie for execute mode."),
    ] = None,
    x_zcsrf_token: Annotated[
        str | None,
        typer.Option("--x-zcsrf-token", help="x-zcsrf-token header."),
    ] = None,
    header: Annotated[
        list[str] | None,
        typer.Option("--header", help="Extra header in KEY=VALUE form."),
    ] = None,
    timeout: Annotated[float, typer.Option("--timeout", min=1.0)] = 30.0,
    show_secrets: Annotated[bool, typer.Option("--show-secrets")] = False,
    credentials_file: Annotated[
        str | None,
        typer.Option(
            "--credentials-file",
            help="Optional .env override path. Defaults to ZOHO_CREDENTIALS_FILE.",
        ),
    ] = None,
) -> None:
    """Build or execute a self-client granttoken request."""

    _load_credentials_env(credentials_file)
    resolved_client_id = self_client_id or os.getenv("ZOHO_SELF_CLIENT_ID")
    if not resolved_client_id:
        raise typer.BadParameter(
            "self-client id is required (--self-client-id or ZOHO_SELF_CLIENT_ID)"
        )

    payload = _build_grant_payload(
        scopes_csv=scopes,
        scope_items=scope,
        expiry=expiry,
        description=description,
        approved_orgs=approved_orgs,
    )
    endpoint = _grant_endpoint(api_console_domain, resolved_client_id)

    if not execute:
        _print_json(
            {
                "mode": "template",
                "endpoint": endpoint,
                "payload": payload,
                "curl_template": _render_grant_curl_template(endpoint, payload),
            }
        )
        return

    if not session_cookie:
        raise typer.BadParameter("--session-cookie is required when using --execute")

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cookie": session_cookie,
        "User-Agent": "zoho-auth-cli/0.1.1",
    }
    if x_zcsrf_token:
        headers["x-zcsrf-token"] = x_zcsrf_token
    headers.update(_parse_extra_headers(header))

    with httpx.Client(timeout=timeout) as http:
        response = http.post(endpoint, headers=headers, json=payload)

    body = _http_response_to_json(response)
    safe = _sanitize_payload(body, show_secrets=show_secrets)
    _print_json(safe)
    if response.status_code >= 400:
        raise typer.Exit(code=1)


@app.command("scope-builder")
def scope_builder(
    product: Annotated[
        list[str] | None,
        typer.Option(
            "--product",
            "-p",
            help="Repeatable product name: CRM, Creator, Projects, People, Sheet, WorkDrive.",
        ),
    ] = None,
    access: Annotated[
        AccessProfile | None,
        typer.Option("--access", help="Scope profile: read, write, or admin."),
    ] = None,
    include_common: Annotated[
        bool | None,
        typer.Option(
            "--include-common/--no-include-common",
            help="Include broader common scope examples for each selected product.",
        ),
    ] = None,
    scope: Annotated[
        list[str] | None,
        typer.Option("--scope", help="Repeatable additional scopes to include."),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option("--interactive/--no-interactive", help="Enable interactive prompts."),
    ] = True,
    output_format: Annotated[
        OutputFormat,
        typer.Option("--format", help="Output format: json, text, or env."),
    ] = OutputFormat.json,
    output_file: Annotated[
        Path | None,
        typer.Option("--output-file", help="Optional path to write output."),
    ] = None,
) -> None:
    """Interactive scope builder for selecting product scope bundles."""

    selected_products = _select_products(preset_products=product, interactive=interactive)
    selected_access = _resolve_access_profile(access=access, interactive=interactive)
    selected_include_common = _resolve_include_common(
        include_common=include_common,
        interactive=interactive,
    )
    extra_scopes = _resolve_additional_scopes(
        additional_scope=scope,
        interactive=interactive,
    )

    scopes_by_product: dict[str, list[str]] = {}
    combined_scopes: list[str] = []

    for selected_product in selected_products:
        product_scopes = _scopes_for_product(
            product=selected_product,
            access=selected_access,
            include_common=selected_include_common,
        )
        scopes_by_product[selected_product] = product_scopes
        combined_scopes.extend(product_scopes)

    combined_scopes.extend(extra_scopes)
    final_scopes = _validate_scope_tokens(_dedupe(combined_scopes))

    payload: dict[str, Any] = {
        "products": selected_products,
        "access_profile": selected_access.value,
        "include_common": selected_include_common,
        "scopes_by_product": scopes_by_product,
        "scope_count": len(final_scopes),
        "scopes": final_scopes,
        "scopes_csv": ",".join(final_scopes),
    }

    rendered = _render_scope_output(payload=payload, output_format=output_format)
    typer.echo(rendered)

    if output_file is not None:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered + "\n", encoding="utf-8")
        typer.echo(f"Wrote scope output to {output_file}")


def main(argv: list[str] | None = None) -> int:
    command_args = argv if argv is not None else sys.argv[1:]
    try:
        app(args=command_args, prog_name="zoho-auth", standalone_mode=False)
    except typer.Exit as exc:
        return int(exc.exit_code)
    except click.ClickException as exc:
        exc.show()
        return int(exc.exit_code)
    except Exception as exc:  # pragma: no cover - top-level safeguard
        typer.echo(f"error: {exc}", err=True)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
