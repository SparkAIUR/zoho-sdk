"""CLI helpers for Zoho OAuth token and self-client grant code workflows."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

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


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _require_credentials_file(path: str | None) -> Path:
    if not path:
        raise ValueError("ZOHO_CREDENTIALS_FILE is required for this command")
    credentials_path = Path(path).expanduser()
    if not credentials_path.is_file():
        raise ValueError(f"Credentials file does not exist: {credentials_path}")
    return credentials_path


def _load_credentials_env(credentials_file: str | None) -> Path:
    resolved = _require_credentials_file(credentials_file or os.getenv("ZOHO_CREDENTIALS_FILE"))
    load_dotenv(dotenv_path=resolved, override=False)
    return resolved


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
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


def _extract_scopes(*, scopes_csv: str | None, scope_items: list[str] | None) -> list[str]:
    scopes: list[str] = []
    if scopes_csv:
        scopes.extend(scope.strip() for scope in scopes_csv.split(",") if scope.strip())
    if scope_items:
        scopes.extend(scope.strip() for scope in scope_items if scope.strip())

    deduped: list[str] = []
    seen: set[str] = set()
    for scope in scopes:
        if scope not in seen:
            deduped.append(scope)
            seen.add(scope)
    return deduped


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
            raise ValueError(f"Invalid --header format: {item!r}. Expected KEY=VALUE.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid --header format: {item!r}. Header key is empty.")
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


def run_exchange_token(args: argparse.Namespace) -> int:
    _load_credentials_env(args.credentials_file)
    client_id = _required_env("ZOHO_CLIENT_ID")
    client_secret = _required_env("ZOHO_CLIENT_SECRET")
    accounts_domain = _resolve_accounts_domain(args.accounts_domain)

    payload: dict[str, str] = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": args.grant_code,
    }
    redirect_uri = args.redirect_uri or os.getenv("ZOHO_REDIRECT_URI")
    if redirect_uri:
        payload["redirect_uri"] = redirect_uri

    token_url = f"{accounts_domain}/oauth/v2/token"
    with httpx.Client(timeout=args.timeout) as http:
        response = http.post(
            token_url,
            data=payload,
            headers={"User-Agent": "zoho-auth-cli/0.1.1"},
        )

    body = _http_response_to_json(response)
    safe = _sanitize_payload(body, show_secrets=args.show_secrets)
    _print_json(safe)
    return 0 if response.status_code < 400 else 1


def _build_grant_payload(args: argparse.Namespace) -> dict[str, Any]:
    scopes = _extract_scopes(scopes_csv=args.scopes, scope_items=args.scope)
    if not scopes:
        raise ValueError("At least one scope is required (--scopes or --scope)")

    grant_payload: dict[str, Any] = {
        "scope": scopes,
        "expiry": args.expiry,
        "description": args.description,
    }
    if args.approved_orgs:
        grant_payload["approvedorgs"] = args.approved_orgs
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


def run_grant_code(args: argparse.Namespace) -> int:
    _load_credentials_env(args.credentials_file)
    self_client_id = args.self_client_id or os.getenv("ZOHO_SELF_CLIENT_ID")
    if not self_client_id:
        raise ValueError("self-client id is required (--self-client-id or ZOHO_SELF_CLIENT_ID)")

    payload = _build_grant_payload(args)
    endpoint = _grant_endpoint(args.api_console_domain, self_client_id)

    if not args.execute:
        _print_json(
            {
                "mode": "template",
                "endpoint": endpoint,
                "payload": payload,
                "curl_template": _render_grant_curl_template(endpoint, payload),
            }
        )
        return 0

    if not args.session_cookie:
        raise ValueError("--session-cookie is required when using --execute")

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cookie": args.session_cookie,
        "User-Agent": "zoho-auth-cli/0.1.1",
    }
    if args.x_zcsrf_token:
        headers["x-zcsrf-token"] = args.x_zcsrf_token
    headers.update(_parse_extra_headers(args.header))

    with httpx.Client(timeout=args.timeout) as http:
        response = http.post(endpoint, headers=headers, json=payload)

    body = _http_response_to_json(response)
    safe = _sanitize_payload(body, show_secrets=args.show_secrets)
    _print_json(safe)
    return 0 if response.status_code < 400 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--credentials-file",
        default=None,
        help="Optional path override for credentials .env file (otherwise ZOHO_CREDENTIALS_FILE).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    exchange = subparsers.add_parser(
        "exchange-token",
        help="Exchange authorization grant code for OAuth tokens.",
    )
    exchange.add_argument(
        "--grant-code", required=True, help="Authorization code from Zoho OAuth flow."
    )
    exchange.add_argument(
        "--accounts-domain",
        default=None,
        help="Optional accounts domain override (defaults by ZOHO_DC).",
    )
    exchange.add_argument(
        "--redirect-uri",
        default=None,
        help="Redirect URI (required for server-based clients if configured).",
    )
    exchange.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")
    exchange.add_argument(
        "--show-secrets",
        action="store_true",
        help="Print full token payload without redaction.",
    )
    exchange.set_defaults(func=run_exchange_token)

    grant = subparsers.add_parser(
        "grant-code",
        help="Build or execute Zoho API Console self-client granttoken request.",
    )
    grant.add_argument("--self-client-id", default=None, help="Zoho self-client identifier.")
    grant.add_argument(
        "--scopes",
        default=None,
        help="Comma-separated scopes (example: ZohoCRM.modules.ALL,ZohoCRM.users.READ).",
    )
    grant.add_argument(
        "--scope",
        action="append",
        default=None,
        help="Repeatable single scope input.",
    )
    grant.add_argument("--expiry", type=int, default=10, help="Grant-code expiry in minutes.")
    grant.add_argument(
        "--description", default="Evaluation of Zoho SDK", help="Grant-code description."
    )
    grant.add_argument("--approved-orgs", default=None, help="Optional approved org id list.")
    grant.add_argument(
        "--api-console-domain",
        default="https://api-console.zoho.com",
        help="API Console domain for self-client endpoint.",
    )
    grant.add_argument(
        "--execute",
        action="store_true",
        help="Execute live request instead of printing template output.",
    )
    grant.add_argument(
        "--session-cookie",
        default=None,
        help="Session cookie for API Console request (required with --execute).",
    )
    grant.add_argument(
        "--x-zcsrf-token",
        default=None,
        help="Optional x-zcsrf-token header for API Console request.",
    )
    grant.add_argument(
        "--header",
        action="append",
        default=None,
        help="Additional header in KEY=VALUE form. Repeat as needed.",
    )
    grant.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")
    grant.add_argument(
        "--show-secrets",
        action="store_true",
        help="Print unredacted response payload.",
    )
    grant.set_defaults(func=run_grant_code)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
