# Zoho OAuth Scope Catalog

Curated scope catalog for products currently supported by this SDK.

Generated from `tools/specs/scopes_catalog.json`.

## Product Scope Summary

| Product | Scope Syntax | Read Bundle | Write Bundle | Docs |
|---|---|---|---|---|
| CRM | `ZohoCRM.<scope_name>.<operation>` | `ZohoCRM.modules.READ`<br>`ZohoCRM.settings.READ`<br>`ZohoCRM.users.READ`<br>`ZohoCRM.org.READ` | `ZohoCRM.modules.ALL`<br>`ZohoCRM.settings.ALL`<br>`ZohoCRM.users.READ`<br>`ZohoCRM.org.READ` | [link](https://www.zoho.com/crm/developer/docs/api/v8/scopes.html)<br>[link](https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html) |
| Creator | `ZohoCreator.<scope_name>.<operation>` | `ZohoCreator.report.READ`<br>`ZohoCreator.meta.form.READ`<br>`ZohoCreator.meta.application.READ` | `ZohoCreator.report.ALL`<br>`ZohoCreator.form.CREATE`<br>`ZohoCreator.meta.application.READ` | [link](https://www.zoho.com/creator/help/api/v2/oauth-overview.html)<br>[link](https://www.zoho.com/creator/help/api/v2.1/get-records.html)<br>[link](https://www.zoho.com/creator/help/api/v2.1/get-fields.html) |
| Projects | `ZohoProjects.<module>.<operation>` | `ZohoProjects.portals.READ`<br>`ZohoProjects.projects.READ`<br>`ZohoProjects.tasks.READ` | `ZohoProjects.projects.ALL`<br>`ZohoProjects.tasks.ALL`<br>`ZohoProjects.tasklists.ALL` | [link](https://projects.zoho.com/api-docs)<br>[link](https://projectsapi.zoho.com/api-docs) |
| People | `ZOHOPEOPLE.<scope_name>.<operation>` | `ZOHOPEOPLE.forms.READ`<br>`ZOHOPEOPLE.employee.ALL` | `ZOHOPEOPLE.forms.ALL`<br>`ZOHOPEOPLE.employee.ALL` | [link](https://www.zoho.com/people/api/scopes.html)<br>[link](https://www.zoho.com/people/api/forms-api/fetch-forms.html) |
| Sheet | `ZohoSheet.<scope_name>.<operation>` | `ZohoSheet.dataAPI.READ` | `ZohoSheet.dataAPI.READ`<br>`ZohoSheet.dataAPI.UPDATE` | [link](https://sheet.zoho.com/help/api/v2/) |
| WorkDrive | `WorkDrive.<scope_name>.<operation>` | `WorkDrive.team.READ`<br>`WorkDrive.files.READ` | `WorkDrive.team.ALL`<br>`WorkDrive.files.ALL` | [link](https://workdrive.zoho.com/apidocs/v1/overview) |

## Product Details

### CRM

- Service prefix: `ZohoCRM`
- Scope syntax: `ZohoCRM.<scope_name>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `ZohoCRM.modules.READ` |
| `ZohoCRM.modules.ALL` |
| `ZohoCRM.settings.READ` |
| `ZohoCRM.settings.ALL` |
| `ZohoCRM.users.READ` |
| `ZohoCRM.org.READ` |
| `ZohoCRM.coql.READ` |
| `ZohoCRM.apis.READ` |

Notes: Use module-specific scopes for least privilege when possible.

References:
- https://www.zoho.com/crm/developer/docs/api/v8/scopes.html
- https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html

### Creator

- Service prefix: `ZohoCreator`
- Scope syntax: `ZohoCreator.<scope_name>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `ZohoCreator.report.READ` |
| `ZohoCreator.report.CREATE` |
| `ZohoCreator.report.UPDATE` |
| `ZohoCreator.report.DELETE` |
| `ZohoCreator.form.CREATE` |
| `ZohoCreator.meta.form.READ` |
| `ZohoCreator.meta.application.READ` |
| `ZohoCreator.dashboard.READ` |

Notes: Creator APIs often split data and metadata scopes.

References:
- https://www.zoho.com/creator/help/api/v2/oauth-overview.html
- https://www.zoho.com/creator/help/api/v2.1/get-records.html
- https://www.zoho.com/creator/help/api/v2.1/get-fields.html

### Projects

- Service prefix: `ZohoProjects`
- Scope syntax: `ZohoProjects.<module>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `ZohoProjects.portals.READ` |
| `ZohoProjects.projects.READ` |
| `ZohoProjects.projects.ALL` |
| `ZohoProjects.tasklists.READ` |
| `ZohoProjects.tasks.READ` |
| `ZohoProjects.tasks.UPDATE` |
| `ZohoProjects.users.READ` |
| `ZohoProjects.search.READ` |
| `ZohoPC.files.CREATE` |

Notes: File attachments may require ZohoPC.files.* and, for WorkDrive-backed portals, WorkDrive.files.*.

References:
- https://projects.zoho.com/api-docs
- https://projectsapi.zoho.com/api-docs

### People

- Service prefix: `ZOHOPEOPLE`
- Scope syntax: `ZOHOPEOPLE.<scope_name>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `ZOHOPEOPLE.forms.READ` |
| `ZOHOPEOPLE.forms.ALL` |
| `ZOHOPEOPLE.employee.ALL` |
| `ZOHOPEOPLE.attendance.ALL` |
| `ZOHOPEOPLE.leave.READ` |
| `ZOHOPEOPLE.timetracker.ALL` |

Notes: People scope names are upper-case service prefix and module-specific scope names.

References:
- https://www.zoho.com/people/api/scopes.html
- https://www.zoho.com/people/api/forms-api/fetch-forms.html

### Sheet

- Service prefix: `ZohoSheet`
- Scope syntax: `ZohoSheet.<scope_name>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `ZohoSheet.dataAPI.READ` |
| `ZohoSheet.dataAPI.UPDATE` |

Notes: Sheet docs show dataAPI READ/UPDATE examples; use least privilege per operation.

References:
- https://sheet.zoho.com/help/api/v2/

### WorkDrive

- Service prefix: `WorkDrive`
- Scope syntax: `WorkDrive.<scope_name>.<operation>`
- Supported operations: `READ, CREATE, UPDATE, DELETE, ALL`

Common scope examples:

| Scope |
|---|
| `WorkDrive.team.ALL` |
| `WorkDrive.files.READ` |
| `WorkDrive.files.CREATE` |
| `WorkDrive.files.UPDATE` |
| `WorkDrive.files.DELETE` |

Notes: WorkDrive scopes are endpoint-specific; admin/team APIs usually require team scopes.

References:
- https://workdrive.zoho.com/apidocs/v1/overview

## Regenerate

```bash
uv run python tools/scopes_sync.py
```

## Build Scope Sets Interactively

Use the CLI scope builder when planning app permissions:

```bash
uv run zoho-auth scope-builder
uv run zoho-auth scope-builder --product CRM --product People --access read --format env
```
