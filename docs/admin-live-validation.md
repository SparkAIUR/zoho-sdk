# Live Credential Validation (Admin)

Use `tools/admin_validate_live.py` to validate live credentials and product scopes before rollout.

The script is designed for administrators and runs **read-only SDK operations** (GET-based product calls) to confirm access is wired correctly.

## 1. Prepare Credentials File

Store credentials in a local `.env` file (for example under `refs/notes/`):

```bash
# refs/notes/zoho-live.env
ZOHO_CLIENT_ID=...
ZOHO_CLIENT_SECRET=...
ZOHO_REFRESH_TOKEN=...
ZOHO_DC=US
ZOHO_ENVIRONMENT=production
```

Optional vars for broader validation:

```bash
ZOHO_PROJECTS_PORTAL_ID=12345678
ZOHO_CREATOR_ACCOUNT_OWNER=your_owner
ZOHO_CREATOR_APP_LINK_NAME=your_app
```

## 2. Run Validator

```bash
export ZOHO_CREDENTIALS_FILE=refs/notes/zoho-live.env
uv sync --group dev
uv run python tools/admin_validate_live.py
```

## What It Checks

- `crm.org.get`
- `crm.modules.list`
- `projects.portals.list`
- `projects.projects.list` (if portal is available)
- `creator.meta.get_forms` (if Creator vars are set)
- `people.forms.list_forms`
- `sheet.workbooks.list`
- `workdrive.admin.list_teams`

## Safety and Output

- Product checks are read-only operations.
- Logs are sanitized: no tokens, secrets, or full payload dumps.
- Results show pass/fail/skip with counts only.

Exit codes:
- `0` success (including skipped optional checks)
- `1` one or more checks failed
- `2` configuration error (missing file or required env vars)
