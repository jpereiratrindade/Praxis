#!/usr/bin/env python3
"""Auto-gate do Praxis Governed Engineering Method 0.1."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from governed_method_schema import load_flat_yaml, load_schema, validate_instance


ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "docs/methodology/GOVERNED_ENGINEERING_METHOD_V0_1.md",
    "policies/governed_project_state_policy.md",
    "contracts/methodology/project-state.schema.json",
    "contracts/methodology/experiment-record.schema.json",
    "templates/governed-project/.hoa/project-state.yaml",
    "scripts/governed_method_schema.py",
    "scripts/validate_governed_project.py",
    "harness/scenarios/PRAXIS-METHOD-001-governed-state.md",
]


def main() -> int:
    errors: list[str] = []

    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing: {relative}")

    if errors:
        print("Praxis governed engineering method: NOT_READY", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    try:
        project_schema = load_schema(
            ROOT / "contracts/methodology/project-state.schema.json"
        )
        experiment_schema = load_schema(
            ROOT / "contracts/methodology/experiment-record.schema.json"
        )
    except Exception as exc:
        print(
            f"Praxis governed engineering method: NOT_READY\n- schema: {exc}",
            file=sys.stderr,
        )
        return 1

    if project_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("project-state schema draft must be 2020-12")
    if experiment_schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("experiment-record schema draft must be 2020-12")

    try:
        template = load_flat_yaml(
            ROOT / "templates/governed-project/.hoa/project-state.yaml"
        )
    except Exception as exc:
        errors.append(f"invalid canonical-state template: {exc}")
        template = {}

    if template:
        errors.extend(
            f"template: {error}"
            for error in validate_instance(template, project_schema)
        )

    experiment_fixture = {
        "experiment": {
            "id": "A0-E001",
            "title": "Example governed experiment",
            "phase": "A0",
            "status": "verified",
        },
        "verification": {"gate": "scripts/verify_a0_e001.sh"},
        "outputs": {
            "evidence": "docs/experiments/evidence/a0-e001/verification.txt",
            "tests": ["tests/example_tests.cpp"],
        },
    }
    errors.extend(
        f"experiment fixture: {error}"
        for error in validate_instance(experiment_fixture, experiment_schema)
    )

    try:
        for relative in [
            "scripts/governed_method_schema.py",
            "scripts/validate_governed_project.py",
            "scripts/validate_methodology_repo.py",
        ]:
            source = (ROOT / relative).read_text(encoding="utf-8")
            ast.parse(source, filename=relative)
    except (OSError, SyntaxError) as exc:
        errors.append(f"validator syntax: {exc}")

    method_text = (
        ROOT / "docs/methodology/GOVERNED_ENGINEERING_METHOD_V0_1.md"
    ).read_text(encoding="utf-8")
    policy_text = (
        ROOT / "policies/governed_project_state_policy.md"
    ).read_text(encoding="utf-8")

    for token in [
        "M01 — Canonical State",
        "M03 — Operational Evidence ≠ Governed Evidence",
        "M04 — Monotonic Bootstrap",
        "M07 — Learning → Rule → Gate",
    ]:
        if token not in method_text:
            errors.append(f"method principle missing: {token}")

    if "praxis-governed-engineering/0.1" not in policy_text:
        errors.append("policy does not bind praxis-governed-engineering/0.1")

    if errors:
        print("Praxis governed engineering method: NOT_READY", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("PASS methodology artifacts")
    print("PASS methodology schemas")
    print("PASS canonical-state template conforms to schema")
    print("PASS experiment-record schema executable fixture")
    print("PASS methodology validators compile")
    print("PASS methodology principles/policy")
    print("\nPraxis governed engineering method v0.1: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
