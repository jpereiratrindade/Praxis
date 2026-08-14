#!/usr/bin/env python3
"""Subset mínimo e sem dependências de JSON Schema usado pelo método Praxis 0.1."""

from __future__ import annotations

import datetime as _datetime
import json
import re
from pathlib import Path
from typing import Any


def parse_scalar(raw: str) -> Any:
    value = raw.strip()

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]

    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None

    return value


def load_flat_yaml(path: Path) -> dict[str, Any]:
    """Lê o subconjunto plano de YAML adotado por project-state.yaml."""
    result: dict[str, Any] = {}

    for number, original in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = original.strip()
        if not line or line.startswith("#"):
            continue

        if original[:1].isspace():
            raise ValueError(
                f"{path}: linha {number}: estado canônico v0.1 deve permanecer plano"
            )

        if ":" not in original:
            raise ValueError(f"{path}: linha {number}: esperado 'chave: valor'")

        key, raw = original.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"{path}: linha {number}: chave vazia")
        if key in result:
            raise ValueError(f"{path}: linha {number}: chave duplicada: {key}")

        result[key] = parse_scalar(raw)

    return result


def load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _type_matches(instance: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(instance, dict)
    if expected == "array":
        return isinstance(instance, list)
    if expected == "string":
        return isinstance(instance, str)
    if expected == "boolean":
        return isinstance(instance, bool)
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if expected == "null":
        return instance is None
    return True


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    *,
    path: str = "$",
) -> list[str]:
    """Valida somente as palavras-chave usadas pelos contratos Method 0.1."""
    errors: list[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: esperado const {schema['const']!r}, obtido {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: valor {instance!r} fora de enum {schema['enum']!r}")

    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _type_matches(instance, expected_type):
        errors.append(
            f"{path}: esperado tipo {expected_type}, obtido {type(instance).__name__}"
        )
        return errors

    if isinstance(instance, dict):
        for required in schema.get("required", []):
            if required not in instance:
                errors.append(f"{path}: campo obrigatório ausente: {required}")

        properties = schema.get("properties", {})
        for key, value in instance.items():
            child = properties.get(key)
            if child is not None:
                errors.extend(validate_instance(value, child, path=f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: propriedade não permitida: {key}")

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(
                    validate_instance(item, item_schema, path=f"{path}[{index}]")
                )

    if isinstance(instance, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(instance) < minimum:
            errors.append(f"{path}: tamanho mínimo {minimum}")

        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, instance) is None:
            errors.append(f"{path}: não satisfaz pattern {pattern!r}")

        if schema.get("format") == "date":
            try:
                _datetime.date.fromisoformat(instance)
            except ValueError:
                errors.append(f"{path}: data ISO inválida: {instance!r}")

    return errors
