"""CRM COQL query operations and fluent query builder."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import TYPE_CHECKING

from zoho.crm.models import CoqlInfo, CoqlQueryResponse

if TYPE_CHECKING:
    from zoho.crm.client import CRMClient

CoqlParam = str | int | float | bool | datetime | date

_PARAM_PATTERN = re.compile(r":([A-Za-z_][A-Za-z0-9_]*)")
_SELECT_PATTERN = re.compile(r"\bselect\b", flags=re.IGNORECASE)
_FROM_PATTERN = re.compile(r"\bfrom\b", flags=re.IGNORECASE)
_LIMIT_PATTERN = re.compile(r"\blimit\b", flags=re.IGNORECASE)


def _validate_query_shape(query: str) -> str:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise ValueError("COQL query must not be empty.")
    if _SELECT_PATTERN.search(cleaned_query) is None or _FROM_PATTERN.search(cleaned_query) is None:
        raise ValueError("COQL query must include both SELECT and FROM clauses.")
    return cleaned_query


def _serialize_param(value: CoqlParam) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        escaped = value.isoformat().replace("'", "''")
        return f"'{escaped}'"
    if isinstance(value, date):
        escaped = value.isoformat().replace("'", "''")
        return f"'{escaped}'"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _bind_query_params(query: str, params: Mapping[str, CoqlParam] | None) -> str:
    placeholders = {match.group(1) for match in _PARAM_PATTERN.finditer(query)}
    if not placeholders:
        return query
    if not params:
        missing = ", ".join(sorted(placeholders))
        raise ValueError(f"Missing COQL parameter values for: {missing}")

    missing_keys: set[str] = set()

    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in params:
            missing_keys.add(key)
            return match.group(0)
        return _serialize_param(params[key])

    rendered = _PARAM_PATTERN.sub(_replace, query)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"Missing COQL parameter values for: {missing}")
    return rendered


def _parse_response(payload: Mapping[str, object]) -> CoqlQueryResponse:
    data_raw = payload.get("data")
    data = (
        [item for item in data_raw if isinstance(item, dict)] if isinstance(data_raw, list) else []
    )

    info_raw = payload.get("info")
    info = CoqlInfo.model_validate(info_raw) if isinstance(info_raw, dict) else None
    return CoqlQueryResponse(data=data, info=info)


class CoqlClient:
    """COQL operations for Zoho CRM."""

    def __init__(self, crm_client: CRMClient) -> None:
        self._crm = crm_client

    async def execute(
        self,
        *,
        query: str,
        params: Mapping[str, CoqlParam] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> CoqlQueryResponse:
        rendered_query = _bind_query_params(_validate_query_shape(query), params)
        payload = await self._crm.request(
            "POST",
            "/coql",
            json={"select_query": rendered_query},
            headers=headers,
        )
        return _parse_response(payload)

    async def execute_all(
        self,
        *,
        query: str,
        params: Mapping[str, CoqlParam] | None = None,
        batch_size: int = 2000,
        start_offset: int = 0,
        max_records: int = 100_000,
        headers: Mapping[str, str] | None = None,
    ) -> CoqlQueryResponse:
        if batch_size < 1 or batch_size > 2000:
            raise ValueError("batch_size must be between 1 and 2000.")
        if start_offset < 0:
            raise ValueError("start_offset must be >= 0.")
        if max_records < 1:
            raise ValueError("max_records must be >= 1.")

        base_query = _bind_query_params(_validate_query_shape(query), params)
        if _LIMIT_PATTERN.search(base_query) is not None:
            raise ValueError(
                "execute_all() does not accept queries that already include LIMIT. "
                "Remove LIMIT and control paging with batch_size/start_offset."
            )

        all_rows: list[dict[str, object]] = []
        current_offset = start_offset

        while len(all_rows) < max_records:
            remaining = max_records - len(all_rows)
            page_size = min(batch_size, remaining)
            paged_query = f"{base_query} limit {current_offset}, {page_size}"
            response = await self.execute(query=paged_query, headers=headers)
            page_rows = response.data
            all_rows.extend(page_rows[:remaining])

            more_records = bool(response.info.more_records) if response.info is not None else False
            if not more_records:
                break
            if not page_rows:
                break
            current_offset += len(page_rows)

        return CoqlQueryResponse(
            data=all_rows,
            info=CoqlInfo(count=len(all_rows), more_records=False),
        )

    def select(self, *fields: str) -> CoqlQueryBuilder:
        return CoqlQueryBuilder(_client=self).select(*fields)


@dataclass(frozen=True, slots=True)
class CoqlQueryBuilder:
    """Immutable fluent builder for COQL queries."""

    _client: CoqlClient
    _select_fields: tuple[str, ...] = ()
    _from_module: str | None = None
    _where_clauses: tuple[str, ...] = ()
    _where_params: tuple[tuple[str, CoqlParam], ...] = ()
    _order_terms: tuple[str, ...] = ()
    _limit: int | None = None
    _offset: int | None = None

    def select(self, *fields: str) -> CoqlQueryBuilder:
        clean_fields = tuple(field.strip() for field in fields if field.strip())
        if not clean_fields:
            raise ValueError("select() requires at least one field.")
        return replace(self, _select_fields=self._select_fields + clean_fields)

    def from_(self, module: str) -> CoqlQueryBuilder:
        clean_module = module.strip()
        if not clean_module:
            raise ValueError("from_() requires a non-empty module name.")
        return replace(self, _from_module=clean_module)

    def where(
        self,
        predicate: str,
        *,
        params: Mapping[str, CoqlParam] | None = None,
    ) -> CoqlQueryBuilder:
        clean_predicate = predicate.strip()
        if not clean_predicate:
            raise ValueError("where() requires a non-empty predicate.")
        merged_params = self._merge_params(params)
        return replace(
            self,
            _where_clauses=(*self._where_clauses, clean_predicate),
            _where_params=merged_params,
        )

    def where_eq(self, field: str, value: CoqlParam) -> CoqlQueryBuilder:
        clean_field = field.strip()
        if not clean_field:
            raise ValueError("where_eq() requires a non-empty field.")
        return self.where(f"{clean_field} = {_serialize_param(value)}")

    def where_in(self, field: str, values: Sequence[CoqlParam]) -> CoqlQueryBuilder:
        clean_field = field.strip()
        if not clean_field:
            raise ValueError("where_in() requires a non-empty field.")
        rendered_values = tuple(_serialize_param(value) for value in values)
        if not rendered_values:
            raise ValueError("where_in() requires at least one value.")
        return self.where(f"{clean_field} in ({', '.join(rendered_values)})")

    def where_is_null(self, field: str) -> CoqlQueryBuilder:
        clean_field = field.strip()
        if not clean_field:
            raise ValueError("where_is_null() requires a non-empty field.")
        return self.where(f"{clean_field} is null")

    def where_is_not_null(self, field: str) -> CoqlQueryBuilder:
        clean_field = field.strip()
        if not clean_field:
            raise ValueError("where_is_not_null() requires a non-empty field.")
        return self.where(f"{clean_field} is not null")

    def order_by(self, *terms: str) -> CoqlQueryBuilder:
        clean_terms = tuple(term.strip() for term in terms if term.strip())
        if not clean_terms:
            raise ValueError("order_by() requires at least one sort term.")
        return replace(self, _order_terms=self._order_terms + clean_terms)

    def limit(self, value: int) -> CoqlQueryBuilder:
        if value < 1 or value > 2000:
            raise ValueError("limit() must be between 1 and 2000.")
        return replace(self, _limit=value)

    def offset(self, value: int) -> CoqlQueryBuilder:
        if value < 0:
            raise ValueError("offset() must be >= 0.")
        return replace(self, _offset=value)

    def to_query(self) -> str:
        if not self._select_fields:
            raise ValueError("Builder query requires at least one selected field.")
        if self._from_module is None:
            raise ValueError("Builder query requires from_(module).")

        query = f"select {', '.join(self._select_fields)} from {self._from_module}"
        if self._where_clauses:
            query += " where " + " and ".join(f"({clause})" for clause in self._where_clauses)
        if self._order_terms:
            query += f" order by {', '.join(self._order_terms)}"
        if self._offset is not None and self._limit is None:
            raise ValueError("offset() requires limit() for valid COQL LIMIT syntax.")
        if self._limit is not None:
            if self._offset is None:
                query += f" limit {self._limit}"
            else:
                query += f" limit {self._offset}, {self._limit}"

        return _bind_query_params(query, dict(self._where_params))

    async def execute(self, *, headers: Mapping[str, str] | None = None) -> CoqlQueryResponse:
        return await self._client.execute(query=self.to_query(), headers=headers)

    async def execute_all(
        self,
        *,
        batch_size: int = 2000,
        start_offset: int = 0,
        max_records: int = 100_000,
        headers: Mapping[str, str] | None = None,
    ) -> CoqlQueryResponse:
        return await self._client.execute_all(
            query=self.to_query(),
            batch_size=batch_size,
            start_offset=start_offset,
            max_records=max_records,
            headers=headers,
        )

    def _merge_params(
        self,
        params: Mapping[str, CoqlParam] | None,
    ) -> tuple[tuple[str, CoqlParam], ...]:
        merged = dict(self._where_params)
        if params:
            for key, value in params.items():
                existing = merged.get(key)
                if existing is not None and existing != value:
                    raise ValueError(
                        f"Conflicting value for where() parameter {key!r}: "
                        f"{existing!r} != {value!r}"
                    )
                merged[key] = value
        return tuple(merged.items())
