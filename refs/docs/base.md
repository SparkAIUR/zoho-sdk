Below is how I’d design an **async‑first, high‑performance, DX‑focused** Zoho CRM Python SDK that can be **(re)generated automatically** so you can stay compatible with upstream changes—especially the schema/typing information that Zoho’s SDK already ships (via `json_details.json`) and the official API surface (via Zoho’s OAS files).

---

## 1) First, identify what “the spec” actually is

### What Zoho’s current Python SDK is doing today

Zoho’s current server-side Python SDK:

* is a wrapper around the Zoho CRM REST APIs ([Zoho][1])
* uses OAuth2 and handles token generation/refresh/persistence in SDK code ([Zoho][1])
* depends on the synchronous `requests` stack (docs explicitly require installing `requests`) ([Zoho][2])
* has explicit “Operations” classes per resource (e.g., `AttachmentsOperations`, `RecordOperations`, etc.) in its public DX surface ([Zoho][3])

That lines up with your “current opinion”: the SDK is sync-first and feels dated for modern Python async apps (FastAPI, async workers, etc.).

### What Zoho provides as “officially generateable” API specs

Zoho now also publishes **OpenAPI Specification (OAS) 3.0** files for CRM v8 on GitHub and even documents how to generate client SDKs from them. ([Zoho][4])
They also explicitly warn the OAS is **generic** and won’t encode all module-specific business logic/constraints. ([Zoho][4])

### Where `json_details.json` fits

Zoho’s server-side Python SDK references “a JSON file” that affects parsing/validation and even saving API credits by validating requests earlier. ([Zoho][1])
That JSON file is exactly the kind of artifact you want to treat as a **schema oracle** for *models + parameter typing + validation rules*, so your generated SDK matches Zoho’s own expectations. (Your `json_details.json` link is the right direction.) ([GitHub][5])

**Key practical point:** `json_details.json` is excellent for *types and model/field metadata*, but in practice you’ll still want a second input for *endpoint paths/methods* (OAS or extracted op-defs).

So the design should be **hybrid-spec**:

* **Schema + model metadata** → `json_details.json` (upstream-compat anchor)
* **Endpoints + paths + HTTP methods** → Zoho CRM OAS files (official, stable), optionally cross-checked against upstream SDK operation modules for parity

---

## 2) North Star goals for a “modern” SDK

### Async-first DX

* Every API call is `await`‑able
* No global initialization required
* Works naturally in FastAPI / Starlette / async worker processes
* Supports concurrency (gather, task groups) without thread hacks

### Performance-first

* connection pooling
* streaming downloads/uploads
* fast JSON encoding/decoding (opt-in)
* minimal model overhead

### Best-in-class typing and IDE experience

* typed request parameters, headers, and responses
* autocompletion for resources and methods
* ergonomic pagination
* readable exceptions with response context

### Regenerate, don’t hand-maintain

* “update spec → regenerate → run contract tests → release”
* the generated layer is deterministic, diffable, and reviewable

---

## 3) Library architecture

### Package layout

I’d split into a thin handwritten “core” and a large generated surface:

```
zoho_crm_async/
  __init__.py
  client.py              # AsyncZohoCRMClient (handwritten)
  transport.py           # HTTPX transport, retries, rate limiting
  auth/
    __init__.py
    oauth.py             # OAuth flows + refresh logic
    token_store.py       # Async token store interface + implementations
  errors.py              # rich exceptions
  pagination.py          # async pagers
  middleware.py          # hooks, tracing, logging
  generated/
    __init__.py
    operations/          # generated endpoint clients
    models/              # generated dataclasses / pydantic models
    params/              # generated param/header definitions
  compat/
    __init__.py          # optional: old-style API names/shims
```

### Core client (handwritten): `AsyncZohoCRMClient`

Responsibilities:

* own an async HTTP client
* attach auth headers (OAuth2)
* handle retries, backoff, rate limits
* decode responses and raise consistent exceptions
* dispatch into generated operation modules

#### HTTP library choice

Use **HTTPX** as default transport because it has a mature async client and can share concepts across sync/async if you ever want a sync wrapper. ([python-httpx.org][6])
(You *can* support `aiohttp` as an optional backend, but one default keeps complexity down.) ([docs.aiohttp.org][7])

---

## 4) Public API shape (DX design)

You want two layers:

### A) “Ergonomic” resource API (recommended default)

Example:

```python
from zoho_crm_async import ZohoCRM

async with ZohoCRM.from_refresh_token(
    client_id=...,
    client_secret=...,
    refresh_token=...,
    dc="US",
    environment="PRODUCTION",
) as crm:
    lead = await crm.records("Leads").get(lead_id=123, fields=["Email", "Last_Name"])

    async for rec in crm.records("Leads").iter(page_size=200):
        ...

    await crm.records("Leads").update(lead_id=123, data={"Last_Name": "Ng"})
```

### B) “Upstream compatible” ops API (optional shim)

If you want painless migration, expose a compat layer where the **same class names** exist but methods are async:

```python
from zoho_crm_async.compat import RecordOperations

ops = RecordOperations(module_api_name="Leads", client=crm)
resp = await ops.get_record(123, fields=["Email"])
```

This mirrors Zoho’s existing “Operations class” mental model. ([Zoho][3])

---

## 5) Auth: async-safe, concurrency-safe OAuth2

Zoho’s SDKs are built around OAuth2 and token persistence. ([Zoho][1])
Key modern improvements:

### Async token store interface

Define:

```python
class AsyncTokenStore(Protocol):
    async def load(self, key: str) -> OAuthToken | None: ...
    async def save(self, key: str, token: OAuthToken) -> None: ...
```

Provide:

* `FileTokenStore` (async file IO)
* `SQLiteTokenStore` (aiosqlite)
* `RedisTokenStore` (optional)

### Concurrency-safe refresh

When multiple coroutines hit an expired token at once:

* ensure only **one refresh in flight** (async lock / singleflight)
* others await the refresh result

### Domain + environment correctness

Zoho explicitly notes tokens are **domain-specific and environment-specific** and the SDK will error otherwise. ([Zoho][2])
Encode that into config:

* `dc` (US/EU/IN/CN/AU)
* `environment` (PRODUCTION/SANDBOX/DEVELOPER) ([Zoho][1])
* token store key includes `{dc}:{environment}:{user}` to prevent accidental reuse

---

## 6) Transport: retries, rate limits, and streaming

### Retry strategy (safe by default)

* Retry on transient network errors
* Retry on 429 + `Retry-After` header
* Retry on 5xx with exponential backoff + jitter
* Don’t blindly retry non-idempotent POSTs unless Zoho guarantees idempotency

### Rate limiting

Zoho APIs have quotas/credits. You don’t want uncontrolled concurrency to amplify failures.
Provide:

* global concurrency limit (semaphore)
* optional token bucket rate limiter per org/app

### Streaming downloads/uploads

Make file endpoints stream:

* attachments download
* bulk read export
* large uploads

This matters for performance and memory.

---

## 7) Models & typing: generated from `json_details.json`

This is where you get **upstream compatibility** with Zoho’s own SDK serialization rules.

### What to generate from `json_details.json`

Generate:

1. **Models** (request/response bodies)
2. **Param and header types** (query params, headers)
3. **Enums / Choices** from `values`
4. **Field-level constraints**: required/nullable/emptiable, etc.

The file is explicitly positioned as a “details”/spec-like resource used by the SDK for parsing/validation. ([Zoho][1])

### Model runtime: dataclasses first, validation optional

For performance, default to:

* `@dataclass(slots=True)` models
* fast serialization/deserialization paths

Then offer an optional “validated mode”:

* generate **Pydantic v2** models (or adapters) for people who want strict validation and developer safety. Pydantic v2’s Rust core is notably faster than v1 and can be a reasonable optional layer. ([pydantic.dev][8])

### JSON codec

Use stdlib `json` by default, but offer an optional extra for **orjson** for speed. ([PyPI][9])

### “Choice” type

Zoho uses a `Choice` concept in their SDK; in modern Python:

* generate `Enum` when `values` exist
* else represent as `str | int | ...` with typed wrappers

---

## 8) Endpoints: generated from OAS + cross-checked for parity

Since Zoho publishes OAS and documents code generation from it, it’s a natural source for endpoints. ([Zoho][4])

But because they warn it’s generic, I’d do:

### Hybrid endpoint generation approach

**Input A (primary):** OAS files (paths, methods, parameters, response codes) ([Zoho][4])
**Input B (compat/parity):** upstream Python SDK operation modules (optional “parity pass”)
**Input C (schema):** `json_details.json` for request/response class typing

In codegen:

* build an internal representation (IR) of endpoints from OAS
* map endpoint request/response schemas to `json_details` generated models where possible
* where OAS is generic (e.g., module-specific record shapes), surface as:

  * `dict[str, Any]` + typed “known envelope wrappers”
  * or a dynamic “Record” type

### Why not only OAS?

Because Zoho themselves say those files are generic and don’t fully cover module-specific business logic. ([Zoho][4])
So the SDK should treat OAS as endpoint truth, but treat `json_details` (and real responses) as schema truth.

---

## 9) Code generation pipeline

### Step-by-step pipeline

1. **Fetch upstream inputs**

   * download `json_details.json` from the official SDK repo (or extract from PyPI wheel)
   * download OAS files from Zoho’s `crm-oas` repo ([GitHub][10])

2. **Normalize to an intermediate representation (IR)**

   * `ModelDef`, `FieldDef`, `EnumDef`
   * `EndpointDef` (path, method, params, headers, request body, responses)

3. **Generate code**

   * `generated/models/*.py` from `ModelDef`
   * `generated/operations/*.py` from `EndpointDef`
   * `generated/params/*.py` for named query/header definitions
   * `generated/__init__.py` exports clean surface

4. **Generate documentation**

   * mkdocs or sphinx from the same IR
   * include examples per operation group

5. **Contract tests**

   * golden tests: “generator output matches previous output unless spec changes”
   * runtime tests against mocked HTTP responses
   * optional live tests (gated) for a real Zoho org

6. **Release automation**

   * CI checks for spec changes upstream
   * open PR with regenerated code + changelog
   * tag and publish

### Practical DX: keep generated code readable

Even though it’s generated, make it:

* deterministic ordering
* black/ruff formatted
* human-auditable diffs

---

## 10) Error handling and responses (big DX win)

Zoho’s SDK talks about `APIResponse` and `APIException` vs `SDKException`. ([Zoho][1])
In a modern SDK, I’d keep that idea but make it more Pythonic:

### Exceptions

* `ZohoAPIError(status, code, message, details, request_id, raw)`
* `ZohoAuthError`
* `ZohoRateLimitError(retry_after=...)`
* `ZohoValidationError` (client-side model/param validation)
* `ZohoTransportError` (timeouts, DNS, etc.)

### Response object

Return either:

* parsed model (default)
* or a `Response[T]` wrapper that includes:

  * `data: T`
  * `status_code`
  * `headers`
  * `raw_json`
  * `request_id`

This is extremely helpful for debugging without forcing users to drop into logging.

---

## 11) Pagination: async iterators as first-class

For endpoints with `page` and `per_page` params (Zoho exposes these widely), build:

```python
async for rec in crm.records("Leads").iter(per_page=200):
    ...
```

Internally:

* fetch pages sequentially
* optionally prefetch next page (bounded) for throughput
* support “resume from page_token” where Zoho uses tokens

This is both **DX** and **performance**.

---

## 12) Versioning strategy (avoid breaking users)

Zoho versions their SDKs by API version (v8 etc.) and publishes multiple SDK package versions. ([Zoho][1])

I’d do:

* package major version tracks **API major** (v8)
* SDK semver tracks your wrapper stability
* embed `spec_revision` metadata in the package (commit hash / release date)
* provide a CLI: `zoho-crm-async regen --from upstream` to regenerate against the latest upstream spec

---

## 13) Putting it all together: what I’d actually ship

### Minimal dependencies

Base install:

* `httpx` (async client) ([python-httpx.org][6])
* `anyio` (optional, nice abstraction)
* `python-dateutil` if needed for parsing (Zoho uses date/time heavily)

Extras:

* `zoho-crm-async[orjson]` ([PyPI][9])
* `zoho-crm-async[pydantic]` ([pydantic.dev][8])
* `zoho-crm-async[http2]` (httpx http2 extra) ([python-httpx.org][11])

### Two public surfaces

* `zoho_crm_async.ZohoCRM` (ergonomic, async-first)
* `zoho_crm_async.compat.*` (upstream naming shims)

### Regeneration story

* “spec update” PR includes:

  * updated `json_details.json` snapshot
  * updated OAS snapshot (or pin)
  * regenerated code
  * changelog and breaking changes detection

---

## 14) The biggest design constraint: “compatibility” means choosing what you preserve

You can preserve compatibility at different layers:

1. **Wire compatibility** (most important): correct paths, params, headers, serialization
2. **Model compatibility**: field names/types match upstream SDK’s expectations (json_details-driven)
3. **API surface compatibility**: same classes/method names as Zoho SDK (optional, via `compat/`)

For DX, I’d recommend:

* guarantee (1) and (2)
* provide (3) as a shim, but encourage the new ergonomic API for new code

---

## 15) A short concrete blueprint

If I were implementing this, I’d start with:

1. **Core transport + auth**

   * httpx async client + refresh-token flow
   * token store + concurrency-safe refresh
   * robust errors

2. **Codegen v1**

   * generate models from `json_details.json`
   * generate a small subset of endpoints from OAS (records + modules)
   * add pagination helpers

3. **Parity pass**

   * compare responses and edge cases against Zoho’s current SDK behavior
   * add compat shims for key operations classes

4. **Scale out to full endpoint coverage**

   * import additional OAS resources
   * fill gaps where OAS is generic with dynamic typing

---

If you want, I can also outline:

* an example **IR schema** for codegen (ModelDef/EndpointDef)
* a template strategy (jinja2 vs AST-based generation)
* how I’d map `json_details` “spec_type” values into Python types
* how I’d handle Zoho’s record “dynamic fields” while still giving strong typing where possible

[1]: https://www.zoho.com/crm/developer/docs/sdk/server-side/python-sdk.html "https://www.zoho.com/crm/developer/docs/sdk/server-side/python-sdk.html"
[2]: https://www.zoho.com/crm/developer/docs/server-side-sdks/v2/py-overview.html "https://www.zoho.com/crm/developer/docs/server-side-sdks/v2/py-overview.html"
[3]: https://www.zoho.com/crm/developer/docs/python-sdk/v2/sample-codes.html "https://www.zoho.com/crm/developer/docs/python-sdk/v2/sample-codes.html"
[4]: https://www.zoho.com/crm/developer/docs/api/v8/openapi-specification.html "https://www.zoho.com/crm/developer/docs/api/v8/openapi-specification.html"
[5]: https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/refs/heads/main/zohocrmsdk/src/json_details.json "raw.githubusercontent.com"
[6]: https://www.python-httpx.org/async/ "https://www.python-httpx.org/async/"
[7]: https://docs.aiohttp.org/ "https://docs.aiohttp.org/"
[8]: https://pydantic.dev/articles/pydantic-v2 "https://pydantic.dev/articles/pydantic-v2"
[9]: https://pypi.org/project/orjson/ "https://pypi.org/project/orjson/"
[10]: https://github.com/zoho/crm-oas "GitHub - zoho/crm-oas: ZohoCRM API's OAS Files"
[11]: https://www.python-httpx.org/ "https://www.python-httpx.org/"


---

Below are “guiding-document” style outlines for the four pieces you called out: **(1) a codegen IR**, **(2) template strategy**, **(3) mapping `json_details.json` types into Python**, and **(4) strong typing for Zoho’s dynamic Record fields**.

I’m assuming you want to generate a modern async-first client primarily from:

* Zoho’s **OpenAPI specs** (endpoints/params/request+response schemas) published in `zoho/crm-oas` (e.g., `record.json` is OpenAPI **3.1.0**). ([GitHub][1])
* Zoho’s **`json_details.json`** from the existing Python SDK repo (model field metadata, interface unions, constraints, etc.). ([GitHub][2])

---

## 1) Intermediate Representation schema for code generation

### Goals

1. **Single normalized source of truth** for generation (so codegen is deterministic and diff-friendly).
2. **Lossless-ish**: keep enough provenance from both sources that you can trace any generated class/field/endpoint back to where it came from (OAS JSON Pointer + json_details key).
3. **Supports Zoho-specific modeling** that OpenAPI alone doesn’t capture well:

   * “interface + classes” unions in `json_details.json`
   * field constraints (`values`, `regex`, min/max length)
   * `extend_property` (field variants / “one-of-like” behavior)
   * map “keys” metadata (i.e., typed “details” maps)
4. **Can overlay org-specific schema** (for custom modules/fields) without forking upstream.

Zoho’s OAS files are explicitly intended to support SDK generation and describe endpoints, request/response formats, auth, etc. ([GitHub][1])

---

### Inputs and how they map into IR

#### Input A: Zoho OAS (crm-oas)

Use this as your “endpoint truth”:

* `paths` → operations/endpoints
* `components.parameters` → reusable params
* `components.schemas` → request/response schemas
* `security` per operation → scopes

Example: `record.json` defines `/ {module}` GET/POST/PUT/DELETE with many query parameters and OAuth scopes. ([GitHub][3])

#### Input B: `json_details.json`

Use this as “model truth” for:

* fields, types, constraints, enumerated values
* interface unions (`{"interface": true, "classes":[...]}`)
* field-level metadata (structure_name, sub_type, extend_property, keys, etc.) ([GitHub][2])

You can also use the existing SDK’s `constants.py` as a sanity check for Zoho’s own primitive mapping conventions (e.g., `Long -> int`, `DateTime -> datetime`). ([GitHub][4])

---

### IR: proposed top-level shape

Think in three layers:

1. **Core IR**: language-agnostic-ish representation of endpoints and schemas.
2. **Zoho Extensions**: captures json_details nuances (interfaces, extend_property, Choice values, keys metadata).
3. **Overlays**: org-specific schema overlay to add/override field defs for customizations.

A concrete (JSON-serializable) IR container:

```python
@dataclass(frozen=True)
class IR:
    meta: IRMeta
    types: dict[str, TypeDef]          # "record.Record", "tags.SuccessResponse", etc.
    endpoints: dict[str, EndpointDef]  # "records.getRecords", etc.
    groups: dict[str, GroupDef]        # logical grouping: records, modules, fields, ...
    overlays: list[Overlay]            # optional (org schema)
```

#### IRMeta

* generator version
* upstream OAS version (from `openapi`/`info.version`)
* upstream json_details commit hash / URL
* build timestamp
* compatibility level (“Zoho v8”, “SDK 8.0 mapping”)

---

### IR: Type system model (TypeRef)

You need a type graph that can represent:

* primitives (str/int/float/bool/date/datetime)
* lists and dicts with inner types
* model references
* unions (for “interfaces” and extend_property)
* literals/enums
* file uploads
* “unknown JSON” (Any / JsonValue)

```python
@dataclass(frozen=True)
class TypeRef:
    kind: Literal[
        "primitive", "model", "list", "dict", "union",
        "literal", "enum", "file", "json"
    ]
    # one of:
    primitive: str | None = None          # "str", "int", "datetime", ...
    model_id: str | None = None           # "record.Record"
    item: "TypeRef" | None = None         # for list
    key: "TypeRef" | None = None          # for dict
    value: "TypeRef" | None = None        # for dict
    variants: tuple["TypeRef", ...] = ()  # for union
    literal_values: tuple[str, ...] = ()  # for literal/enum
    # provenance/hints:
    zoho_spec_type: str | None = None     # "TString", ...
    zoho_type: str | None = None          # "Long", "List", ...
```

Notes:

* Keep `zoho_spec_type` + `zoho_type` as *metadata* even if you normalize to Python.
* `kind="json"` is your escape hatch for “unstructured payload”.

---

### IR: Model definitions (TypeDef)

```python
@dataclass(frozen=True)
class TypeDef:
    id: str                     # stable, e.g. "record.Record"
    python_module: str           # "zoho_crm_async.models.record"
    python_name: str             # "Record"
    kind: Literal["object", "alias", "enum", "interface"]
    fields: tuple["FieldDef", ...] = ()
    alias_of: TypeRef | None = None            # for type aliases
    interface_variants: tuple[str, ...] = ()   # model_ids implementing the interface

    provenance: "Provenance" = Provenance()
```

#### FieldDef

```python
@dataclass(frozen=True)
class FieldDef:
    python_name: str             # snake_case
    wire_name: str               # Zoho JSON key / param name (often same as "name" in json_details)
    type: TypeRef
    required: bool
    nullable: bool
    read_only: bool

    constraints: "Constraints" = Constraints()
    provenance: "Provenance" = Provenance()
```

#### Constraints

* allowed values (`values` in json_details)
* regex
* min/max length
* map keys schema (`keys` in json_details for some maps)
* docstring text (from OAS schema description, if present)

---

### IR: Endpoint definitions (EndpointDef)

```python
@dataclass(frozen=True)
class EndpointDef:
    id: str                    # "records.getRecords"
    operation_id: str           # from OAS
    method: Literal["GET","POST","PUT","DELETE","PATCH"]
    path: str                  # "/{module}"
    group: str                 # "records"

    summary: str | None
    description: str | None

    path_params: tuple["ParamDef", ...]
    query_params: tuple["ParamDef", ...]
    header_params: tuple["ParamDef", ...]
    request_body: "RequestBodyDef | None"
    responses: tuple["ResponseDef", ...]

    oauth_scopes: tuple[str, ...]     # normalized union of OAS security requirements
    provenance: "Provenance"
```

This is derived almost entirely from OAS. Example: record GET endpoint uses path `/{module}` and defines parameters like `fields`, `page`, `per_page`, and security scopes. ([GitHub][3])

---

### Provenance (traceability)

You’ll thank yourselves later if every IR node includes:

```python
@dataclass(frozen=True)
class Provenance:
    source: Literal["oas","json_details","overlay","manual"] = "manual"
    oas_file: str | None = None              # "record.json"
    oas_json_pointer: str | None = None      # "/paths/~1{module}/get/..."
    json_details_key: str | None = None      # "zohocrmsdk.src.com.zoho.crm.api.record.Record"
    json_details_field: str | None = None    # "Created_Time"
```

---

### Normalization rules (make generation stable)

1. **Stable IDs**

   * Type IDs: `"{group}.{ClassName}"` where `group` is the Zoho API area (record, tags, fields, …).
   * Endpoint IDs: `"{group}.{operation_id}"`.

2. **Name mapping**

   * `wire_name` should remain exactly the Zoho key (`"Created_Time"`, `"page_token"`, etc.)
   * `python_name` is snake_case transformation + reserved-word handling.

3. **Ordering**

   * Always sort fields and models deterministically (e.g., by wire_name).
   * Always sort endpoints by path+method.

4. **Unification**

   * If OAS defines a schema and json_details defines the “same” model, merge:

     * prefer OAS for required/nullable and structured schema shape
     * prefer json_details for constraints/values/interface/extend_property
   * If they disagree, IR should record both in provenance + expose a “conflict report” during codegen.

---

### Handling Zoho “interfaces” and “extend_property” in IR

* **Interfaces** (json_details root: `{"interface": true, "classes":[...]}`) become:

  * `TypeDef(kind="interface", interface_variants=[...])`
  * and then `TypeRef(kind="union", variants=[ModelRef(...), ...])`

* **extend_property** on a field becomes:

  * `TypeRef(kind="union", variants=[...])`
  * store a “union_reason=extend_property” metadata if you want.

This is crucial because Zoho uses interface unions heavily for “response handlers” like `ActionResponse` → `SuccessResponse | APIException`, etc. ([GitHub][2])

---

## 2) Template strategy: Jinja2 vs AST-based generation

### Why this matters for your project

You’re not just generating “some models”; you’re generating:

* an async HTTP client surface
* hundreds of models
* unions/interfaces
* optional org-specific model overlays

So you want:

* deterministic output
* readable generated code (DX)
* minimal generator complexity (maintainability)
* correctness guarantees

---

### Option A: Jinja2 templates (recommended for “whole-file generation”)

**Jinja2** is a widely used templating engine; it’s fast and designed for rendering text documents from data. ([Jinja][5])

**Pros**

* Very productive for large amounts of boilerplate
* Easy to diff templates and generated code
* Clear file-level control (imports, class layout, docstrings)

**Cons**

* Templates can accrete logic
* Easier to accidentally emit syntactically invalid Python unless you validate

**Best practice if you choose Jinja2**

* Keep templates dumb: no business logic; only presentation.
* Put logic in Python “view models” (objects already normalized from IR).
* After generation:

  1. `ast.parse()` every file (fast syntax validation)
  2. run a formatter (`ruff format`) ([Astral Docs][6])
  3. run lints (`ruff check`) to catch unused imports, etc.

> Ruff’s formatter is explicitly positioned as a fast drop-in replacement for Black, and includes import sorting hooks. ([Astral Docs][6])

---

### Option B: Python `ast` module generation

The standard library `ast` module represents Python source as an Abstract Syntax Tree. ([Python documentation][7])

**Pros**

* Harder to generate invalid Python
* Refactoring is easier because you manipulate structure
* Can be very deterministic

**Cons**

* The code emitter/unparser may not produce the style you want
* More verbose to write than templates
* Docstring formatting, comments, and import layout is fiddly

This is good if you want maximal safety and you’re okay treating formatting as a post-step.

---

### Option C: LibCST generation / codemods (best for patching existing code)

LibCST parses Python into a Concrete Syntax Tree that preserves formatting, comments, whitespace, parentheses, etc. ([LibCST][8])

**Pros**

* Ideal if you need to apply incremental transforms on top of a maintained codebase
* Great for “patch the generated code with codemods”

**Cons**

* Overkill if you always regenerate entire files
* Higher cognitive load for the generator team

---

### Recommended hybrid approach for your SDK

**Use Jinja2 for file layout + a small “Python emitter layer” for tricky bits**, plus strict post-validation:

1. **IR → “render models”** (pure Python objects)

   * these contain: imports, forward refs, class signature, field strings, docstrings, etc.

2. **Render** with Jinja2 (one template per file-type):

   * `models/*.py`
   * `client/*.py`
   * `errors/*.py`
   * `types.py`

3. **Validation**

   * `ast.parse` on each generated file (syntax)
   * optionally `python -m compileall` for extra safety

4. **Formatting**

   * `ruff format` (or black) ([Astral Docs][6])

5. **Static checks**

   * mypy/pyright (on generated stubs)
   * ruff lint for unused imports

Why this is a good fit:

* You’re generating lots of files from scratch (templates excel here).
* You can enforce correctness with AST parsing + formatting.
* You keep the generator simple.

---

### Template file structure suggestion

```
tools/codegen/
  parse_oas.py
  parse_json_details.py
  build_ir.py
  render/
    __init__.py
    model_view.py
    endpoint_view.py
  templates/
    model.py.j2
    enum.py.j2
    client_group.py.j2
    types.py.j2
src/zoho_crm_async/_generated/
  models/
  clients/
  ...
```

Also: emit a header comment like:

```python
# @generated by zoho-crm-async-codegen
# Source: zoho/crm-oas v8.0 + zohocrm-python-sdk-8.0 json_details.json
# Do not edit manually.
```

---

## 3) Mapping `json_details.json` `spec_type` values to Python types

### What you have to map

Zoho’s `json_details.json` field entries carry both:

* `spec_type` like `com.zoho.api.spec.template.type.TString`
* `type` like `String`, `Long`, `List`, `Map`, or a fully qualified structure name
* and sometimes `sub_type`, `keys`, `values`, `regex`, `min_length`, `max_length`, `extend_property`, `interface`.

The current `json_details.json` file is the authoritative source for these per-field entries. ([GitHub][2])

Zoho’s own SDK also maps common types in `constants.py` (e.g., `Long: int`, `DateTime: datetime`, `Date: date`). ([GitHub][4])

---

### Canonical Python types you should target

Define a small set of SDK “wire primitives”:

```python
from __future__ import annotations
from datetime import date, datetime, time
from typing import Any, TypeAlias

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
```

And then build everything else from these.

---

### Suggested `spec_type` → Python mapping

Based on the patterns in Zoho’s SDK mappings and what appears in `json_details.json`, here’s a practical mapping table:

| `spec_type`    | Meaning (practical)                                     | Python type                                                                |
| -------------- | ------------------------------------------------------- | -------------------------------------------------------------------------- |
| `TString`      | string                                                  | `str`                                                                      |
| `TBoolean`     | boolean                                                 | `bool`                                                                     |
| `TInteger`     | 32-bit-ish integer                                      | `int`                                                                      |
| `TLong`        | 64-bit-ish integer                                      | `int`                                                                      |
| `TLongString`  | “long id” often treated as long-but-string in some SDKs | `int` (accept `str` on input + coerce)                                     |
| `TDouble`      | floating point                                          | `float` (optionally `Decimal` for money, but you’d need field-level hints) |
| `TDate`        | date                                                    | `datetime.date`                                                            |
| `TDateTime`    | date-time                                               | `datetime.datetime`                                                        |
| `TTimeZone`    | timezone                                                | `str` (IANA name) or `zoneinfo.ZoneInfo` (optional conversion)             |
| `TCollections` | list/collection                                         | `list[T]`                                                                  |
| `TArray`       | array                                                   | `list[T]`                                                                  |
| `TMap`         | map/object                                              | `dict[str, T]` **or** `TypedDict`/model if keys known                      |
| `TObject`      | arbitrary JSON                                          | `JsonValue` or `Any`                                                       |
| `TSerial`      | serial integer                                          | `int`                                                                      |
| `TFile`        | file upload                                             | `UploadFile` abstraction (see below)                                       |

Notes and citations:

* Zoho’s SDK maps `"Long": int`, `"DateTime": datetime`, `"Date": date` in `DATA_TYPE`. ([GitHub][4])
* Their file upload concept uses a `StreamWrapper` class. ([GitHub][9])

---

### File type: recommend a modern abstraction

Zoho’s existing SDK uses a `StreamWrapper` holding `(name, stream/path)` for file transfer. ([GitHub][9])

In a modern async-first SDK, you can expose something like:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

@dataclass(frozen=True)
class UploadFile:
    filename: str
    data: bytes | BinaryIO | Path
    content_type: str | None = None
```

Then your request builder can stream it via multipart form.

---

### How to interpret `sub_type` for lists and maps

`json_details.json` often uses:

* `type: "List"` + `sub_type: {"type": "..."}`
* `type: "Map"` + `sub_type` and sometimes `sub_type_1` for key/value

Algorithmic rule:

1. If `spec_type` is `TCollections` or `TArray`:

   * item type is in `sub_type["type"]`
   * if `structure: true`, item is a model reference (`structure_name`)
   * else it’s a primitive token (`String`, `Integer`, `Object`, etc.)

2. If `spec_type` is `TMap`:

   * if `keys` exists: generate a dedicated typed structure (TypedDict/model) for those keys (more below)
   * else:

     * key is almost always `str`
     * value type:

       * use `sub_type_1["type"]` if present, else `JsonValue`

This is where TypedDict shines, because it’s literally “dict with specific string keys and specific value types.” ([typing.python.org][10])

---

### `values` and `Choice`: how to generate enums/literals safely

You will frequently see `values: [...]` in `json_details.json` for fields like status, code, etc.

You have 3 reasonable options:

**Option 1 (best for typing DX): `Literal[...]`**

* Great completions
* Zero runtime overhead

```python
from typing import Literal
MailFormat = Literal["html", "text"]
```

**Option 2 (best for runtime docs/printability): `Enum`**

* Nicely named symbols, but you must decide how to handle unknown values

**Option 3 (hybrid, “accept unknown”): `str` + Annotated metadata**

* Keep runtime permissive, keep hints for IDEs/docs.

If you use Pydantic for request/response models, you can enforce allowed values when you want; Pydantic models are designed for typed fields + validation/serialization. ([Pydantic][11])

---

### Maps with known keys: generate a TypedDict or model

Some `TMap` fields include a `keys` list describing allowed keys and their types.

For example, many `APIException.details` maps have structured key information (expected_data_type, api_name, json_path, etc.). This is exactly the use case for TypedDict. ([typing.python.org][10])

Rule:

* If a map has `keys`, generate a new `TypeDef` like `{ParentType}{FieldName}Map` and set the field type to that model.

---

### Interfaces and unions: generate `TypeAlias` unions

`json_details.json` uses interface definitions a lot (e.g., ResponseHandler/ActionResponse patterns). Treat them as:

```python
from typing import TypeAlias

ActionResponse: TypeAlias = SuccessResponse | APIException
```

If you use Pydantic, note it can parse unions, and it supports “dynamic model creation” (useful for the Record typing strategy later). ([Pydantic][11])

---

### `extend_property`: treat as union (but keep provenance)

If a field has `extend_property`, represent it as a union type in IR, and keep metadata showing *why* it’s a union.

At runtime:

* If you decode responses into typed models, you may need a “try variants in order” parsing strategy (or a discriminator if Zoho provides one, often they don’t).

---

## 4) Handling Zoho Record dynamic fields with strong typing

This is the biggest DX lever, because Zoho records are **module-dependent** and **org-customizable**.

### What Zoho’s current SDK does (and what it implies)

In Zoho’s Python SDK record samples:

* For known “standard” fields, they guide users to use `Field.<Module>.<field>()` constants (good autocomplete).
* For **custom fields**, they explicitly instruct using `record.add_key_value("Custom_field", value)` where the string is the field API name. ([Zoho][12])

That’s your proof that:

* The SDK must support arbitrary keys (open-world record schema).
* Strong typing can’t be fully solved from static upstream specs alone.

---

### Proposed 3-tier strategy (practical + great DX)

#### Tier 1: A generic `Record` that is always correct

This is your “works everywhere” base.

Key properties:

* behaves like `MutableMapping[str, JsonValue]`
* retains known system fields as real attributes (id, created_time, modified_time, etc.)
* stores all other fields in an internal dict

Example API:

```python
record = Record()
record["Last_Name"] = "Smith"        # always works
record["Custom_Field"] = 123         # always works
```

This matches Zoho’s own “add_key_value” idea. ([Zoho][12])

DX improvement: add typed helpers:

```python
T = TypeVar("T")

@dataclass(frozen=True)
class FieldDef(Generic[T]):
    api_name: str
    python_name: str
    type: type[T] | Any

record.set(Field.Leads.last_name, "Smith")  # type-checkable
```

(You can still keep `record["..."]` for escape hatches.)

---

#### Tier 2: Runtime schema introspection (strong typing without codegen)

Use Zoho “metadata APIs” to fetch the schema for a module at runtime:

* **Fields Meta Data API** (field definitions; includes `api_name`, `data_type`, `json_type`, picklist values, etc.). ([Zoho][13])
* **Layouts Meta Data API** (which fields are required per layout, sections, etc.). ([Zoho][14])
* **Modules Meta Data API** (module API names, plural labels, etc.). ([Zoho][15])

With that, you can build a `SchemaRegistry`:

```python
schema = await client.schema.get_module_schema("Leads")
lead = schema.new_record()
lead["Last_Name"] = "Smith"               # validated as str
lead["Annual_Revenue"] = 123              # validated as int/float depending on metadata
```

**What you gain**

* runtime validation (optional)
* runtime conversion (date/datetime parsing, numeric coercion, etc.)
* “discoverability”: users can introspect available fields and picklist options

**How to make it “typed”**

* expose `schema.fields` as `dict[str, FieldDef[Any]]`
* and allow `schema.field("Last_Name")` to return a `FieldDef[str]` when metadata indicates it

If you choose Pydantic for this layer, you can generate a dynamic model per module (`create_model`) with field aliases mapping to Zoho API names; Pydantic explicitly supports model-based schemas and dynamic model creation patterns. ([Pydantic][11])

Also: keep it async-first; the schema fetch calls are network-bound, so your registry should be async-aware and cached.

---

#### Tier 3: Org-specific codegen (“best possible DX”)

This is how you get IDE autocomplete for **custom fields**, which upstream specs can’t provide.

Provide a CLI like:

* `zoho-crm-async schema pull --modules Leads Contacts --out schema.json`

  * calls Modules/Fields/Layouts metadata endpoints
* `zoho-crm-async schema generate --in schema.json --out src/my_org_zoho_models/`

  * generates:

    * `LeadsRecord`, `ContactsRecord`, etc.
    * `LeadsFields` constants
    * optional enums for picklists
    * TypedDict/Pydantic/dataclass models (your choice)

**Key design choice:** generate with **field aliases** so serialization always uses Zoho API field names.

Example in Pydantic terms (conceptually):

* Python attr: `last_name`
* wire alias: `"Last_Name"`

This gives:

* ergonomic Python attribute access
* correct Zoho payloads

(And you can still allow extra fields for forward compatibility.)

TypedDict is also an option for record payload typing because it’s explicitly designed for dicts with specific string keys and typed values, and it supports optional vs required keys. ([typing.python.org][10])

---

### Handling “required fields” for records (the hard truth)

Record requiredness varies by:

* module
* layout
* field settings
* org customization

So:

* **OAS-required** fields are not enough.
* **json_details.required_for** is mostly not a reliable “create/update requiredness” signal for Record fields.

Recommended approach:

* Use **Layouts Meta Data** to determine required fields for a chosen layout (or “default” layout) and expose:

  * `schema.required_fields_for_create(layout_id=...)` ([Zoho][14])
* In generated org models:

  * mark required fields as non-optional **for that layout**
  * provide a “strict vs lax” mode

---

### Field type mapping for org schema (high-level)

Fields metadata includes `data_type`/`json_type` (and picklist values, lookups, etc.). ([Zoho][13])

You’ll want a mapping layer like:

* text/email/phone/url → `str`
* integer → `int`
* currency/decimal → `Decimal` (optional)
* boolean → `bool`
* date → `date`
* datetime → `datetime`
* picklist → `Literal[...]` or `Enum`
* multiselectpicklist → `list[str]` (or `set[str]` in Python layer but serialize list)
* lookup/userlookup → small typed object (e.g., `{id:int, name:str|None}`)
* subform → `list[SubformRow]`

This is independent of upstream `json_details` and is what unlocks “custom module strong typing”.

---

## Putting it together: how these four pieces integrate

If you implement the IR correctly, the rest becomes straightforward:

1. **Parse OAS → endpoints + baseline schemas**
   (Zoho publishes OAS per resource group; `record.json` is an example.) ([GitHub][3])

2. **Parse json_details → richer model metadata**

   * constraints, interface unions, map key schemas ([GitHub][2])

3. **Merge → IR**

   * stable IDs + provenance
   * conflict reporting

4. **Generate**

   * templates (Jinja2) ([Jinja][5])
   * validate via `ast.parse` ([Python documentation][7])
   * format via `ruff format` ([Astral Docs][6])

5. **Runtime schema layer**

   * optional “org schema overlay” via metadata APIs (fields/layouts/modules). ([Zoho][13])

6. **Async-first HTTP layer**

   * Use an async-capable client (e.g., HTTPX AsyncClient) as the transport. ([HTTPX][16])

---

## If you want one “decision matrix” recommendation

* **IR:** do it (it’s the unlock for maintainable codegen).
* **Templates:** Jinja2 + `ast.parse` + `ruff format` is the sweet spot for full regeneration. ([Jinja][5])
* **Type mapping:** normalize to Python primitives, preserve Zoho `spec_type` metadata, generate unions/interfaces/literals when safe.
* **Record typing:** implement Tier 1 immediately, Tier 2 next, Tier 3 as the “killer DX” feature.

If you want, I can turn this into a repo-ready “spec document” format (e.g., `docs/architecture/codegen-ir.md`, `docs/architecture/record-typing.md`) with acceptance criteria and concrete test cases (golden IR snapshots, schema pull tests, etc.).

[1]: https://github.com/zoho/crm-oas "GitHub - zoho/crm-oas: ZohoCRM API's OAS Files"
[2]: https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/refs/heads/main/zohocrmsdk/src/json_details.json "https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/refs/heads/main/zohocrmsdk/src/json_details.json"
[3]: https://raw.githubusercontent.com/zoho/crm-oas/main/v8.0/record.json "raw.githubusercontent.com"
[4]: https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/main/zohocrmsdk/src/com/zoho/crm/api/util/constants.py "raw.githubusercontent.com"
[5]: https://jinja.palletsprojects.com/ "Jinja — Jinja Documentation (3.1.x)"
[6]: https://docs.astral.sh/ruff/formatter/ "The Ruff Formatter | Ruff"
[7]: https://docs.python.org/3/library/ast.html "ast — Abstract syntax trees — Python 3.14.3 documentation"
[8]: https://libcst.readthedocs.io/ "LibCST — LibCST  documentation"
[9]: https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/main/zohocrmsdk/src/com/zoho/crm/api/util/stream_wrapper.py "https://raw.githubusercontent.com/zoho/zohocrm-python-sdk-8.0/main/zohocrmsdk/src/com/zoho/crm/api/util/stream_wrapper.py"
[10]: https://typing.python.org/en/latest/spec/typeddict.html "Typed dictionaries — typing  documentation"
[11]: https://docs.pydantic.dev/latest/concepts/models/ "Models - Pydantic Validation"
[12]: https://www.zoho.com/crm/developer/docs/python-sdk/v1/record-samples.html "Record Operation Samples - Python SDK | Online Help - Zoho CRM"
[13]: https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html "https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html"
[14]: https://www.zoho.com/crm/developer/docs/api/v8/layouts-meta.html "https://www.zoho.com/crm/developer/docs/api/v8/layouts-meta.html"
[15]: https://www.zoho.com/crm/developer/docs/api/v8/module-meta.html "https://www.zoho.com/crm/developer/docs/api/v8/module-meta.html"
[16]: https://www.python-httpx.org/async/?utm_source=chatgpt.com "Async Support"
