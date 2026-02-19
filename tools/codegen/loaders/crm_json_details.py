"""Load CRM model metadata from Zoho json_details.json."""

from __future__ import annotations

import json
from pathlib import Path

from tools.codegen.ir import ModelDef


def load_models(path: Path) -> tuple[list[ModelDef], int, dict[str, int]]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("json_details must be a JSON object")

    models: list[ModelDef] = []
    total_field_count = 0
    spec_type_counts: dict[str, int] = {}

    for key in sorted(data):
        value = data[key]
        if not isinstance(value, dict):
            continue

        is_interface = bool(value.get("interface") is True)
        fields = [
            field_value
            for field_value in value.values()
            if isinstance(field_value, dict)
            and (
                "type" in field_value
                or "spec_type" in field_value
                or "structure_name" in field_value
            )
        ]

        for field_value in fields:
            spec_type = field_value.get("spec_type")
            if isinstance(spec_type, str):
                spec_type_counts[spec_type] = spec_type_counts.get(spec_type, 0) + 1

        models.append(
            ModelDef(
                id=key,
                field_count=len(fields),
                interface=is_interface,
            )
        )
        total_field_count += len(fields)

    return models, total_field_count, spec_type_counts
