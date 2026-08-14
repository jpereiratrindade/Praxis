#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED = [
    ".hoa/project.yaml",
    "CONTRIBUTING.md",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    "policies/ai_usage_policy.md",
    "policies/approval_matrix.md",
    "policies/context_boundary_policy.md",
    "policies/evidence_and_audit_policy.md",
    "policies/read_only_dashboard_policy.md",
    "docs/adr/ADR-0001-native-cpp23-core.md",
    "docs/adr/ADR-0002-read-only-observation-dashboard.md",
    "docs/architecture/DDD.md",
    "docs/dai/DAI.md",
    "mcp/contracts/operation_registry_tool_contract.md",
    "examples/evidence_log.json",
    "harness/skills/dashboard.observe.yaml",
    "harness/scenarios/HOA-EXP-002-dashboard-read-only.md",
    "web/index.html",
    "web/assets/app.css",
    "web/assets/app.js",
    "contracts/targets/target.schema.json",
    "policies/external_authority_policy.md",
    "docs/adr/ADR-0003-external-targets-plan-only-actions.md",
    "harness/scenarios/HOA-EXP-003-external-observation.md",
    "contracts/workspace/project-workspace.schema.json",
    "policies/praxis_identity_policy.md",
    "docs/adr/ADR-0005-praxis-product-identity.md",
    "docs/architecture/PRAXIS.md",
    "docs/methodology/GOVERNED_ENGINEERING_METHOD_V0_1.md",
    "policies/governed_project_state_policy.md",
    "templates/governed-project/.hoa/project-state.yaml",
    "scripts/governed_method_schema.py",
    "scripts/validate_governed_project.py",
    "scripts/validate_methodology_repo.py",
    "harness/scenarios/PRAXIS-METHOD-001-governed-state.md",
]

SCHEMAS = [
    "contracts/operations/agent.schema.json",
    "contracts/operations/skill.schema.json",
    "contracts/operations/operation-plan.schema.json",
    "contracts/operations/execution-receipt.schema.json",
    "contracts/methodology/project-state.schema.json",
    "contracts/methodology/experiment-record.schema.json",
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"missing: {relative}")

    for relative in SCHEMAS:
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing: {relative}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {relative}: {exc}")

    agents = sorted((ROOT / "harness/agents").glob("*.yaml"))
    skills = sorted((ROOT / "harness/skills").glob("*.yaml"))
    if len(agents) < 2:
        errors.append("at least two registered agents are required")
    if len(skills) < 9:
        errors.append("at least nine registered skills are required")

    if errors:
        print("Governance baseline: NOT_READY", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Governance baseline: READY ({len(agents)} agents, {len(skills)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
