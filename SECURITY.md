# Security Policy

## Scope

This repository contains SDK code, docs, examples, and tooling for Zoho integrations.
No production credentials, tokens, or customer data should ever be committed.

## Reporting a Vulnerability

- Do not open public issues for suspected vulnerabilities.
- Email the maintainers listed in `pyproject.toml` with:
  - impact summary
  - affected files/versions
  - reproduction details
  - suggested remediation (if available)

We aim to acknowledge reports within 3 business days.

## Pre-Release Security Checklist

Run before making the repository public or cutting a release:

```bash
uv run python tools/security_scan.py --mode all --report .security/secrets-report.json
uv run python tools/admin_validate_live.py  # optional live env validation
```

CI and release workflows also run the security scan and fail on findings.

## Secret Exposure Response

If a secret is detected:

1. Revoke/rotate the credential immediately with Zoho or the relevant provider.
2. Remove the secret from current files and tests.
3. Rewrite git history if the secret was committed.
4. Force-push rewritten history and invalidate all leaked values.
5. Re-run `tools/security_scan.py` to confirm a clean state.
6. Document the incident and remediation in internal notes.

## Credential Handling Rules

- Keep live credentials in local files outside git tracking (for example `refs/notes/*.env`).
- Use explicit runtime inputs (`client_id`, `client_secret`, `refresh_token`) and never log raw token values.
- Prefer redacted output paths in CLI and admin tools.
