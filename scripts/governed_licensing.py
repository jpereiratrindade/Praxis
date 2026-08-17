#!/usr/bin/env python3
"""Deterministic engineering-policy checks for governed project licensing."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from governed_method_schema import load_flat_yaml, load_schema, validate_instance


PRAXIS_ROOT = Path(__file__).resolve().parents[1]
STATE_RELATIVE = Path(".hoa/licensing.yaml")
CAPABILITY_RELATIVE = Path(".hoa/initial-constitution")
CAPABILITY_VALUE = "praxis-initial-constitution/0.1"
POLICY = "praxis-new-project-license/0.1"
POLICY_DEFAULT = "GPL-3.0-or-later"
ARTIFACT_RELATIVE = Path("LICENSE")
SCHEMA = PRAXIS_ROOT / "contracts/methodology/licensing-state.schema.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_licensing_state(root: Path) -> dict[str, Any]:
    return load_flat_yaml(root / STATE_RELATIVE)


def validate_licensing(root: Path) -> tuple[str, list[str]]:
    """Return capability status and bounded coherence errors without mutation."""
    state_path = root / STATE_RELATIVE
    capability_path = root / CAPABILITY_RELATIVE

    if not state_path.exists():
        if capability_path.exists():
            try:
                capability = capability_path.read_text(encoding="utf-8").strip()
            except OSError as exc:
                return "pending", [f"initial-constitution capability unreadable: {exc}"]
            if capability != CAPABILITY_VALUE:
                return "pending", ["initial-constitution capability is invalid"]
            return "pending", []
        return "legacy", []

    errors: list[str] = []
    if capability_path.exists():
        errors.append("initial-constitution capability was not consumed")

    try:
        state = load_licensing_state(root)
        schema = load_schema(SCHEMA)
    except Exception as exc:
        return "constituted", errors + [f"licensing state/schema parse: {exc}"]

    errors.extend(validate_instance(state, schema))
    provenance = state.get("provenance")
    resolved = state.get("resolved")
    rationale = state.get("exception_rationale")

    if provenance == "default" and resolved != POLICY_DEFAULT:
        errors.append("default provenance must resolve the policy default")
    if provenance == "exception":
        if not isinstance(rationale, str) or not rationale.strip():
            errors.append("policy exception requires a non-empty rationale")
    elif rationale is not None:
        errors.append("exception rationale is only valid for exception provenance")

    artifact = root / ARTIFACT_RELATIVE
    if not artifact.is_file():
        errors.append("governed LICENSE artifact is missing")
        return "constituted", errors

    expected_hash = state.get("artifact_sha256")
    observed_hash = sha256(artifact)
    if isinstance(expected_hash, str) and observed_hash != expected_hash:
        errors.append(
            f"LICENSE SHA-256 mismatch: expected {expected_hash}, observed {observed_hash}"
        )

    text = artifact.read_text(encoding="utf-8", errors="replace")
    markers = re.findall(r"(?m)^SPDX-License-Identifier:\s*(\S.*?)\s*$", text)
    if not markers:
        errors.append("LICENSE must declare SPDX-License-Identifier")
    elif len(markers) != 1:
        errors.append("LICENSE must contain exactly one SPDX-License-Identifier")
    elif isinstance(resolved, str):
        declared = markers[0]
        if declared != resolved:
            errors.append(
                f"LICENSE SPDX declaration {declared!r} contradicts resolved {resolved!r}"
            )

    return "constituted", errors


def render_state(
    *, resolved: str, provenance: str, artifact_sha256: str, rationale: str | None
) -> str:
    lines = [
        'version: "0.1"',
        f"resolved: {resolved}",
        f"provenance: {provenance}",
        f"policy: {POLICY}",
        f"policy_default: {POLICY_DEFAULT}",
    ]
    if rationale is not None:
        escaped = rationale.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'exception_rationale: "{escaped}"')
    lines.extend(
        [
            f"artifact: {ARTIFACT_RELATIVE}",
            f"artifact_sha256: {artifact_sha256}",
        ]
    )
    return "\n".join(lines) + "\n"
