#!/usr/bin/env python3
"""Independent adversarial audit generator for PRAXIS-PBG-001."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts/validate_governed_project.py"
SCHEMA_PATH = ROOT / "contracts/methodology/project-state.schema.json"
HELPER_PATH = ROOT / "scripts/governed_method_schema.py"
FIELDS = (
    "last_verified_milestone",
    "last_verified_commit",
    "last_verified_gate",
    "last_verified_evidence",
)
EMPTY = ("NONE", "0000000", "NONE", "NONE")


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("audit_schema_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Praxis schema helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER = load_helper()
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
OFFICIAL = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def command(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, cwd=root, text=True, capture_output=True, check=False
    )


def require(root: Path, *argv: str) -> str:
    result = command(root, *argv)
    if result.returncode != 0:
        raise RuntimeError(f"{argv!r} failed:\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def render_state(state: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in state.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif value is None:
            rendered = "null"
        elif key in {"version", "last_verified_commit", "updated_on"}:
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def base_state(project: str = "audit-fixture") -> dict[str, Any]:
    return {
        "version": "1.0",
        "project": project,
        "governance_method": "praxis-governed-engineering/0.1",
        "phase": "A0",
        "status": "active",
        **dict(zip(FIELDS, EMPTY, strict=True)),
        "next_milestone": "A0",
        "next_milestone_status": "active",
        "next_milestone_authorized": True,
        "updated_on": "2026-08-15",
    }


def write_state(root: Path, state: dict[str, Any]) -> None:
    (root / ".hoa").mkdir(parents=True, exist_ok=True)
    (root / ".hoa/project-state.yaml").write_text(
        render_state(state), encoding="utf-8"
    )


def init_git(root: Path) -> None:
    require(root, "git", "init", "-b", "main")
    require(root, "git", "config", "user.name", "Independent Audit")
    require(root, "git", "config", "user.email", "audit@invalid")


def commit_all(root: Path, message: str) -> str:
    require(root, "git", "add", "-A")
    require(root, "git", "commit", "-m", message)
    return require(root, "git", "rev-parse", "HEAD")


def write_artifacts(
    root: Path,
    milestone: str = "A0",
    *,
    gate: str = "scripts/verify_a0.sh",
    evidence: str = "docs/evidence/a0/verification.txt",
    gate_text: str = "#!/bin/sh\nexit 0\n",
    evidence_text: str | None = None,
    checksum: str | None = None,
) -> tuple[str, str]:
    gate_path = root / gate
    evidence_path = root / evidence
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(gate_text, encoding="utf-8")
    evidence_path.write_text(
        evidence_text if evidence_text is not None else f"{milestone} PASS\n",
        encoding="utf-8",
    )
    if checksum is not None:
        evidence_path.with_suffix(".sha256").write_text(
            checksum + "  verification.txt\n", encoding="utf-8"
        )
    return gate, evidence


def established_state(
    anchor: str,
    *,
    milestone: str = "A0",
    gate: str = "scripts/verify_a0.sh",
    evidence: str = "docs/evidence/a0/verification.txt",
) -> dict[str, Any]:
    state = base_state()
    state.update(
        {
            "last_verified_milestone": milestone,
            "last_verified_commit": anchor,
            "last_verified_gate": gate,
            "last_verified_evidence": evidence,
            "next_milestone": "A1",
            "next_milestone_status": "proposed",
            "next_milestone_authorized": False,
        }
    )
    return state


def schema_results(state: dict[str, Any]) -> tuple[str, str, bool]:
    helper_ok = not HELPER.validate_instance(state, SCHEMA)
    official_ok = not list(OFFICIAL.iter_errors(state))
    return (
        "ACCEPT" if helper_ok else "REJECT",
        "ACCEPT" if official_ok else "REJECT",
        helper_ok == official_ok,
    )


def validator_result(root: Path) -> dict[str, Any]:
    result = command(root, sys.executable, str(VALIDATOR), str(root))
    return {
        "result": "ACCEPT" if result.returncode == 0 else "REJECT",
        "exit_status": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def history_classification(state: dict[str, Any]) -> str:
    occupancy = tuple(state.get(key) == empty for key, empty in zip(FIELDS, EMPTY))
    if all(occupancy):
        return "EMPTY"
    if any(occupancy):
        return "PARTIAL"
    return "ESTABLISHED"


def make_anchor(root: Path, *, artifacts: bool = True) -> str:
    init_git(root)
    write_state(root, base_state())
    if artifacts:
        write_artifacts(root)
    return commit_all(root, "audit anchor")


def exhaustive_tuple_matrix(fixtures: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number in range(16):
        pattern = f"{number:04b}"
        root = fixtures / f"tuple-{pattern}"
        root.mkdir()
        anchor = make_anchor(root)
        populated = ("A0", anchor, "scripts/verify_a0.sh", "docs/evidence/a0/verification.txt")
        values = tuple(
            populated[index] if bit == "1" else EMPTY[index]
            for index, bit in enumerate(pattern)
        )
        state = base_state(pattern)
        state.update(dict(zip(FIELDS, values, strict=True)))
        write_state(root, state)
        helper, official, parity = schema_results(state)
        observed = validator_result(root)
        semantic = "EMPTY" if pattern == "0000" else "ESTABLISHED" if pattern == "1111" else "INVALID_PARTIAL"
        rows.append(
            {
                "pattern": pattern,
                "schema_helper": helper,
                "schema_draft_2020_12": official,
                "schema_parity": parity,
                "lifecycle_classification": history_classification(state),
                "expected_semantic_classification": semantic,
                "validator": observed["result"],
                "validator_exit_status": observed["exit_status"],
            }
        )
    return rows


def schema_feature_cross_validation() -> list[dict[str, Any]]:
    cases = [
        ("oneOf_exactly_one", "y", {"oneOf": [{"type": "string"}, {"const": "x"}]}),
        ("oneOf_zero", 7, {"oneOf": [{"type": "string"}, {"const": "x"}]}),
        ("oneOf_multiple", "x", {"oneOf": [{"type": "string"}, {"const": "x"}]}),
        ("not_success", "y", {"not": {"const": "x"}}),
        ("not_failure", "x", {"not": {"const": "x"}}),
        (
            "nested_used_shape_empty",
            dict(zip(FIELDS, EMPTY, strict=True)),
            {"oneOf": SCHEMA["oneOf"]},
        ),
        (
            "nested_used_shape_partial",
            {
                **dict(zip(FIELDS, EMPTY, strict=True)),
                "last_verified_milestone": "A0",
            },
            {"oneOf": SCHEMA["oneOf"]},
        ),
        ("malformed_type", 7, {"type": "string", "not": {"const": "x"}}),
    ]
    rows: list[dict[str, Any]] = []
    for identity, instance, schema in cases:
        helper = not HELPER.validate_instance(instance, schema)
        official = not list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance)
        )
        rows.append(
            {
                "id": identity,
                "helper": "ACCEPT" if helper else "REJECT",
                "draft_2020_12": "ACCEPT" if official else "REJECT",
                "agreement": helper == official,
            }
        )
    return rows


Mutation = Callable[[Path, dict[str, Any], str], dict[str, Any]]


def adversarial_case(
    fixtures: Path,
    identity: str,
    mutation: Mutation,
    *,
    artifacts_in_anchor: bool = True,
) -> dict[str, Any]:
    root = fixtures / f"established-{identity}"
    root.mkdir()
    anchor = make_anchor(root, artifacts=artifacts_in_anchor)
    state = established_state(anchor)
    state = mutation(root, state, anchor)
    write_state(root, state)
    helper, official, parity = schema_results(state)
    observed = validator_result(root)
    return {
        "id": identity,
        "schema_helper": helper,
        "schema_draft_2020_12": official,
        "schema_parity": parity,
        "validator": observed["result"],
        "exit_status": observed["exit_status"],
        "diagnostic": (observed["stderr"] or observed["stdout"]).strip().splitlines()[-1],
    }


def established_adversarial(fixtures: Path) -> list[dict[str, Any]]:
    def unchanged(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        return state

    def missing_gate(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        (root / state["last_verified_gate"]).unlink()
        return state

    def directory_gate(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_gate"] = "scripts"
        return state

    def missing_evidence(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        (root / state["last_verified_evidence"]).unlink()
        return state

    def directory_evidence(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_evidence"] = "docs/evidence/a0"
        return state

    def wrong_evidence(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        (root / state["last_verified_evidence"]).write_text("A1 PASS\n", encoding="utf-8")
        return state

    def bad_checksum(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        evidence = root / state["last_verified_evidence"]
        evidence.with_suffix(".sha256").write_text("0" * 64 + "  verification.txt\n", encoding="utf-8")
        return state

    def failing_gate(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        (root / state["last_verified_gate"]).write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        return state

    def malformed_commit(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_commit"] = "not-a-commit"
        return state

    def nonexistent_commit(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_commit"] = "deadbee"
        return state

    def inconsistent_milestone(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_milestone"] = "A9"
        (root / state["last_verified_evidence"]).write_text("A9 PASS\n", encoding="utf-8")
        return state

    def untracked_proof(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        write_artifacts(root)
        return state

    def absolute_external_proof(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        external = root.parent / f"{root.name}-external"
        external.mkdir()
        gate = external / "gate.sh"
        evidence = external / "evidence.txt"
        gate.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        evidence.write_text("A0 PASS\n", encoding="utf-8")
        state["last_verified_gate"] = str(gate)
        state["last_verified_evidence"] = str(evidence)
        return state

    def placeholder_values(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        gate, evidence = write_artifacts(
            root,
            "UNKNOWN",
            gate="UNKNOWN_GATE",
            evidence="UNKNOWN_EVIDENCE",
        )
        state["last_verified_milestone"] = "UNKNOWN"
        state["last_verified_gate"] = gate
        state["last_verified_evidence"] = evidence
        return state

    def zero_variant(root: Path, state: dict[str, Any], anchor: str) -> dict[str, Any]:
        state["last_verified_commit"] = "00000000"
        return state

    definitions = [
        ("valid", unchanged, True),
        ("malformed_commit", malformed_commit, True),
        ("nonexistent_commit", nonexistent_commit, True),
        ("missing_gate", missing_gate, True),
        ("directory_gate", directory_gate, True),
        ("missing_evidence", missing_evidence, True),
        ("directory_evidence", directory_evidence, True),
        ("evidence_for_different_milestone", wrong_evidence, True),
        ("invalid_evidence_checksum", bad_checksum, True),
        ("failing_gate_with_pass_text", failing_gate, True),
        ("milestone_inconsistent_with_phase", inconsistent_milestone, True),
        ("untracked_gate_and_evidence", untracked_proof, False),
        ("absolute_external_gate_and_evidence", absolute_external_proof, True),
        ("legacy_placeholder_values", placeholder_values, True),
        ("arbitrary_zero_commit", zero_variant, True),
    ]
    return [
        adversarial_case(fixtures, identity, mutation, artifacts_in_anchor=tracked)
        for identity, mutation, tracked in definitions
    ]


def lifecycle_case(
    fixtures: Path,
    identity: str,
    construct: Callable[[Path], None],
    expected: str,
) -> dict[str, Any]:
    root = fixtures / f"lifecycle-{identity}"
    root.mkdir()
    construct(root)
    observed = validator_result(root)
    return {
        "transition": identity,
        "expected": expected,
        "validator": observed["result"],
        "matches_expected": observed["result"] == expected,
        "diagnostic": (observed["stderr"] or observed["stdout"]).strip().splitlines()[-1],
    }


def lifecycle_matrix(fixtures: Path) -> list[dict[str, Any]]:
    def empty_empty(root: Path) -> None:
        make_anchor(root, artifacts=False)
        state = base_state()
        state["updated_on"] = "2026-08-16"
        write_state(root, state)
        commit_all(root, "remain empty")

    def empty_established(root: Path) -> None:
        anchor = make_anchor(root)
        write_state(root, established_state(anchor))
        commit_all(root, "establish A0")

    def established_established(root: Path) -> None:
        anchor = make_anchor(root)
        write_state(root, established_state(anchor))
        commit_all(root, "establish A0")
        gate, evidence = write_artifacts(
            root,
            "A1",
            gate="scripts/verify_a1.sh",
            evidence="docs/evidence/a1/verification.txt",
        )
        a1_anchor = commit_all(root, "anchor A1 proof")
        state = established_state(a1_anchor, milestone="A1", gate=gate, evidence=evidence)
        state["next_milestone"] = "A2"
        write_state(root, state)
        commit_all(root, "establish A1")

    def established_empty(root: Path) -> None:
        anchor = make_anchor(root)
        write_state(root, established_state(anchor))
        commit_all(root, "establish A0")
        write_state(root, base_state())
        commit_all(root, "regress to empty")

    def empty_partial(root: Path) -> None:
        make_anchor(root)
        state = base_state()
        state["last_verified_milestone"] = "A0"
        write_state(root, state)
        commit_all(root, "commit partial")

    def partial_established(root: Path) -> None:
        init_git(root)
        write_artifacts(root)
        partial = base_state()
        partial["last_verified_milestone"] = "A0"
        write_state(root, partial)
        anchor = commit_all(root, "commit partial")
        write_state(root, established_state(anchor))
        commit_all(root, "move partial to established")

    def established_partial(root: Path) -> None:
        anchor = make_anchor(root)
        write_state(root, established_state(anchor))
        commit_all(root, "establish A0")
        partial = base_state()
        partial["last_verified_milestone"] = "A0"
        write_state(root, partial)
        commit_all(root, "move established to partial")

    def partial_empty(root: Path) -> None:
        init_git(root)
        partial = base_state()
        partial["last_verified_milestone"] = "A0"
        write_state(root, partial)
        commit_all(root, "commit partial")
        write_state(root, base_state())
        commit_all(root, "move partial to empty")

    def established_rollback(root: Path) -> None:
        anchor = make_anchor(root)
        a0 = established_state(anchor)
        write_state(root, a0)
        commit_all(root, "establish A0")
        gate, evidence = write_artifacts(
            root,
            "A1",
            gate="scripts/verify_a1.sh",
            evidence="docs/evidence/a1/verification.txt",
        )
        a1_anchor = commit_all(root, "anchor A1 proof")
        a1 = established_state(a1_anchor, milestone="A1", gate=gate, evidence=evidence)
        a1["next_milestone"] = "A2"
        write_state(root, a1)
        commit_all(root, "establish A1")
        write_state(root, a0)
        commit_all(root, "roll back established tuple to A0")

    definitions = [
        ("EMPTY_TO_EMPTY", empty_empty, "ACCEPT"),
        ("EMPTY_TO_ESTABLISHED", empty_established, "ACCEPT"),
        ("ESTABLISHED_TO_ESTABLISHED", established_established, "ACCEPT"),
        ("ESTABLISHED_TO_EMPTY", established_empty, "REJECT"),
        ("EMPTY_TO_PARTIAL", empty_partial, "REJECT"),
        ("PARTIAL_TO_ESTABLISHED", partial_established, "REJECT"),
        ("ESTABLISHED_TO_PARTIAL", established_partial, "REJECT"),
        ("PARTIAL_TO_EMPTY", partial_empty, "REJECT"),
        ("ESTABLISHED_ROLLBACK", established_rollback, "REJECT"),
    ]
    return [lifecycle_case(fixtures, *definition) for definition in definitions]


def git_orthogonality(fixtures: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    no_head = fixtures / "git-no-head"
    no_head.mkdir()
    init_git(no_head)
    write_state(no_head, base_state())
    rows.append({"case": "initialized_no_HEAD", **validator_result(no_head)})

    history = fixtures / "git-history"
    history.mkdir()
    make_anchor(history, artifacts=False)
    (history / "provenance.txt").write_text("one\n", encoding="utf-8")
    commit_all(history, "provenance one")
    (history / "provenance.txt").write_text("two\n", encoding="utf-8")
    commit_all(history, "provenance two")
    require(history, "git", "switch", "-c", "feature/audit")
    require(history, "git", "remote", "add", "origin", "https://invalid.example/audit.git")
    (history / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    rows.append({"case": "multiple_commits_feature_branch_remote_dirty", **validator_result(history)})

    no_git = fixtures / "git-absent"
    no_git.mkdir()
    write_state(no_git, base_state())
    rows.append({"case": "no_git_repository", **validator_result(no_git)})

    for row in rows:
        row["diagnostic"] = (row["stderr"] or row["stdout"]).strip().splitlines()[-1]
        del row["stdout"]
        del row["stderr"]
    return rows


def cross_artifact_consistency(fixtures: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    empty_root = fixtures / "cross-empty-verified-manifest"
    empty_root.mkdir()
    init_git(empty_root)
    write_state(empty_root, base_state())
    manifest = {
        "experiment": {"id": "A0-E001", "title": "Contradiction", "phase": "A0", "status": "verified"},
        "verification": {"gate": "scripts/verify_a0.sh"},
        "outputs": {"evidence": "docs/evidence/a0/verification.txt", "tests": []},
    }
    manifest_path = empty_root / ".hoa/experiments/A0-E001.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    commit_all(empty_root, "empty state with verified manifest")
    rows.append({"case": "EMPTY_with_verified_experiment_manifest", **validator_result(empty_root)})

    mismatch_root = fixtures / "cross-established-mismatch"
    mismatch_root.mkdir()
    anchor = make_anchor(mismatch_root)
    write_state(mismatch_root, established_state(anchor))
    manifest["experiment"]["id"] = "A1-E001"
    manifest["experiment"]["phase"] = "A1"
    manifest_path = mismatch_root / ".hoa/experiments/A1-E001.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    commit_all(mismatch_root, "established state with contradictory manifest")
    rows.append({"case": "ESTABLISHED_A0_with_verified_A1_manifest", **validator_result(mismatch_root)})

    for row in rows:
        row["diagnostic"] = (row["stderr"] or row["stdout"]).strip().splitlines()[-1]
        del row["stdout"]
        del row["stderr"]
    return rows


def legacy_sentinels() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    variants: list[tuple[str, dict[str, Any]]] = [
        ("nulls", dict(zip(FIELDS, (None, None, None, None), strict=True))),
        ("empty_strings", dict(zip(FIELDS, ("", "", "", ""), strict=True))),
        ("lowercase_none", dict(zip(FIELDS, ("none", "0000000", "none", "none"), strict=True))),
        ("missing_field", {key: value for key, value in zip(FIELDS, EMPTY, strict=True) if key != "last_verified_gate"}),
    ]
    for identity, values in variants:
        state = base_state()
        for field in FIELDS:
            state.pop(field, None)
        state.update(values)
        helper, official, parity = schema_results(state)
        rows.append(
            {
                "case": identity,
                "schema_helper": helper,
                "schema_draft_2020_12": official,
                "schema_parity": parity,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="praxis-pbg-independent-audit-") as temporary:
        fixtures = Path(temporary)
        result = {
            "artifact": "praxis-pbg-001-independent-candidate-audit/0.1",
            "candidate_head": require(ROOT, "git", "rev-parse", "HEAD"),
            "validator_sha256": hashlib.sha256(VALIDATOR.read_bytes()).hexdigest(),
            "schema_sha256": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
            "schema_helper_sha256": hashlib.sha256(HELPER_PATH.read_bytes()).hexdigest(),
            "tuple_matrix": exhaustive_tuple_matrix(fixtures),
            "schema_feature_cross_validation": schema_feature_cross_validation(),
            "established_adversarial": established_adversarial(fixtures),
            "lifecycle_matrix": lifecycle_matrix(fixtures),
            "git_orthogonality": git_orthogonality(fixtures),
            "cross_artifact_consistency": cross_artifact_consistency(fixtures),
            "legacy_sentinels": legacy_sentinels(),
        }

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
