#!/usr/bin/env python3
"""Controlled Praxis P1 observations for PRAXIS-GVI-001."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INSTRUMENT = Path(__file__).resolve()
VALIDATOR = ROOT / "scripts/validate_governed_project.py"
SCHEMA_HELPER = ROOT / "scripts/governed_method_schema.py"
PROJECT_SCHEMA = ROOT / "contracts/methodology/project-state.schema.json"
EXPERIMENT_SCHEMA = ROOT / "contracts/methodology/experiment-record.schema.json"
sys.path.insert(0, str(ROOT / "scripts"))
from governed_method_schema import load_schema, validate_instance  # noqa: E402


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def command(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, cwd=root, text=True, capture_output=True, check=False
    )


def require(root: Path, *argv: str) -> str:
    result = command(root, *argv)
    if result.returncode != 0:
        raise RuntimeError(f"{argv!r} failed:\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def init_repo(root: Path) -> None:
    require(root, "git", "init", "-b", "main")
    require(root, "git", "config", "user.name", "Praxis GVI Fixture")
    require(root, "git", "config", "user.email", "gvi-fixture@invalid")


def commit_all(root: Path, message: str) -> str:
    require(root, "git", "add", "-A")
    require(root, "git", "commit", "-m", message)
    return require(root, "git", "rev-parse", "HEAD")


def commit_paths(root: Path, message: str, *paths: str) -> str:
    require(root, "git", "add", "--", *paths)
    require(root, "git", "commit", "-m", message)
    return require(root, "git", "rev-parse", "HEAD")


def state_dict(
    milestone: str,
    verified_commit: str,
    gate: str,
    evidence: str,
    *,
    phase: str | None = None,
    next_milestone: str | None = None,
) -> dict[str, Any]:
    return {
        "version": "1.0",
        "project": "gvi-fixture",
        "governance_method": "praxis-governed-engineering/0.1",
        "phase": phase or milestone,
        "status": "active",
        "last_verified_milestone": milestone,
        "last_verified_commit": verified_commit,
        "last_verified_gate": gate,
        "last_verified_evidence": evidence,
        "next_milestone": next_milestone or f"{milestone}-NEXT",
        "next_milestone_status": "proposed",
        "next_milestone_authorized": False,
        "updated_on": "2026-08-15",
    }


def render_flat_yaml(state: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in state.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif key in {"version", "last_verified_commit", "updated_on"}:
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def write_state(root: Path, state: dict[str, Any]) -> None:
    path = root / ".hoa/project-state.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_flat_yaml(state), encoding="utf-8")


def write_gate(root: Path, relative: str, exit_status: int = 0) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/bin/sh\nexit {exit_status}\n", encoding="utf-8")
    path.chmod(0o755)
    return path


def write_evidence(root: Path, relative: str, text: str = "A0 PASS\n") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def write_checksum(evidence: Path, digest: str | None = None) -> Path:
    checksum = evidence.with_suffix(".sha256")
    checksum.write_text(
        (digest or sha256_file(evidence)) + f"  {evidence.name}\n",
        encoding="utf-8",
    )
    return checksum


def run_validator(root: Path) -> dict[str, Any]:
    result = command(root, sys.executable, str(VALIDATOR), str(root))
    return {
        "classification": "ACCEPT" if result.returncode == 0 else "REJECT",
        "exit_status": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_gate(root: Path, declared: str) -> dict[str, Any]:
    path = Path(declared)
    if not path.is_absolute():
        path = root / path
    result = command(root, "/bin/sh", str(path))
    return {
        "exit_status": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "succeeds": result.returncode == 0,
    }


def within(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def git_blob(root: Path, revision: str, relative: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def artifact_facts(
    root: Path, declared: str, claimed_commit: str
) -> dict[str, Any]:
    declared_path = Path(declared)
    resolved = declared_path if declared_path.is_absolute() else root / declared_path
    is_internal = within(root, resolved)
    relative = None
    if is_internal:
        relative = str(resolved.resolve().relative_to(root.resolve()))
    tracked = False
    claimed_blob = None
    if relative is not None:
        tracked = command(root, "git", "ls-files", "--error-unmatch", "--", relative).returncode == 0
        claimed_blob = git_blob(root, claimed_commit, relative)
    current = resolved.read_bytes() if resolved.is_file() else None
    return {
        "declared": declared,
        "resolved": str(resolved.resolve()),
        "inside_repository": is_internal,
        "is_file": resolved.is_file(),
        "tracked_at_HEAD": tracked,
        "present_at_claimed_commit": claimed_blob is not None,
        "current_sha256": sha256_bytes(current) if current is not None else None,
        "claimed_commit_sha256": sha256_bytes(claimed_blob) if claimed_blob is not None else None,
        "current_matches_claimed_commit": current is not None
        and claimed_blob is not None
        and current == claimed_blob,
    }


def initialize_source(root: Path) -> str:
    init_repo(root)
    (root / "source.txt").write_text("governed source\n", encoding="utf-8")
    return commit_all(root, "source anchor")


def finish_provenance_case(
    root: Path,
    identity: str,
    claimed_commit: str,
    gate: str,
    evidence: str,
) -> dict[str, Any]:
    result = run_validator(root)
    return {
        "id": identity,
        "claimed_verified_commit": claimed_commit,
        "HEAD": require(root, "git", "rev-parse", "HEAD"),
        "gate": artifact_facts(root, gate, claimed_commit),
        "evidence": artifact_facts(root, evidence, claimed_commit),
        "direct_gate_execution": run_gate(root, gate),
        "validator": result,
        "working_tree": require(root, "git", "status", "--porcelain", "--untracked-files=all"),
    }


def provenance_observations(fixtures: Path) -> list[dict[str, Any]]:
    gate = "scripts/verify_a0.sh"
    evidence = "docs/evidence/a0/verification.txt"
    rows: list[dict[str, Any]] = []

    root = fixtures / "provenance-tracked-at-commit"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("governed source\n", encoding="utf-8")
    write_gate(root, gate)
    write_evidence(root, evidence)
    anchor = commit_all(root, "source and proof anchor")
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_all(root, "record A0 verification")
    rows.append(finish_provenance_case(root, "tracked_at_claimed_commit", anchor, gate, evidence))

    root = fixtures / "provenance-tracked-later"
    root.mkdir()
    anchor = initialize_source(root)
    write_gate(root, gate)
    write_evidence(root, evidence)
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_all(root, "add proof after claimed source commit")
    rows.append(finish_provenance_case(root, "tracked_only_after_claimed_commit", anchor, gate, evidence))

    root = fixtures / "provenance-untracked-gate"
    root.mkdir()
    anchor = initialize_source(root)
    write_gate(root, gate)
    write_evidence(root, evidence)
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_paths(root, "record state without gate", ".hoa/project-state.yaml", evidence)
    rows.append(finish_provenance_case(root, "untracked_gate", anchor, gate, evidence))

    root = fixtures / "provenance-untracked-evidence"
    root.mkdir()
    anchor = initialize_source(root)
    write_gate(root, gate)
    write_evidence(root, evidence)
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_paths(root, "record state without evidence", ".hoa/project-state.yaml", gate)
    rows.append(finish_provenance_case(root, "untracked_evidence", anchor, gate, evidence))

    root = fixtures / "provenance-external-gate"
    root.mkdir()
    anchor = initialize_source(root)
    external = fixtures / "external-gate.sh"
    external.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    evidence_path = write_evidence(root, evidence)
    write_state(root, state_dict("A0", anchor, str(external), evidence))
    commit_paths(root, "record external gate", ".hoa/project-state.yaml", str(evidence_path.relative_to(root)))
    rows.append(finish_provenance_case(root, "external_gate", anchor, str(external), evidence))

    root = fixtures / "provenance-external-evidence"
    root.mkdir()
    anchor = initialize_source(root)
    gate_path = write_gate(root, gate)
    external = fixtures / "external-evidence.txt"
    external.write_text("A0 PASS\n", encoding="utf-8")
    write_state(root, state_dict("A0", anchor, gate, str(external)))
    commit_paths(root, "record external evidence", ".hoa/project-state.yaml", str(gate_path.relative_to(root)))
    rows.append(finish_provenance_case(root, "external_evidence", anchor, gate, str(external)))

    root = fixtures / "provenance-mutated-gate"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("governed source\n", encoding="utf-8")
    gate_path = write_gate(root, gate, 0)
    write_evidence(root, evidence)
    anchor = commit_all(root, "source and proof anchor")
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_all(root, "record verification")
    gate_path.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    rows.append(finish_provenance_case(root, "gate_bytes_changed_after_claim", anchor, gate, evidence))

    root = fixtures / "provenance-mutated-evidence"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("governed source\n", encoding="utf-8")
    write_gate(root, gate)
    evidence_path = write_evidence(root, evidence, "A0 PASS original\n")
    anchor = commit_all(root, "source and proof anchor")
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_all(root, "record verification")
    evidence_path.write_text("A0 PASS replacement\n", encoding="utf-8")
    rows.append(finish_provenance_case(root, "evidence_bytes_changed_after_claim", anchor, gate, evidence))
    return rows


def coherence_case(
    fixtures: Path,
    identity: str,
    *,
    gate_exit: int,
    evidence_text: str,
    checksum: str,
) -> dict[str, Any]:
    root = fixtures / f"coherence-{identity}"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("governed source\n", encoding="utf-8")
    gate = "scripts/verify_a0.sh"
    evidence = "docs/evidence/a0/verification.txt"
    gate_path = write_gate(root, gate, gate_exit)
    evidence_path = write_evidence(root, evidence, evidence_text)
    checksum_path = None
    if checksum == "valid":
        checksum_path = write_checksum(evidence_path)
    elif checksum == "invalid":
        checksum_path = write_checksum(evidence_path, "0" * 64)
    anchor = commit_all(root, "source and proof anchor")
    write_state(root, state_dict("A0", anchor, gate, evidence))
    commit_all(root, "record verification")
    validator = run_validator(root)
    return {
        "id": identity,
        "gate_sha256": sha256_file(gate_path),
        "evidence_sha256": sha256_file(evidence_path),
        "checksum": checksum,
        "checksum_path": str(checksum_path.relative_to(root)) if checksum_path else None,
        "direct_gate_execution": run_gate(root, gate),
        "evidence_text": evidence_text,
        "validator": validator,
    }


def coherence_observations(fixtures: Path) -> list[dict[str, Any]]:
    return [
        coherence_case(fixtures, "success_pass_no_checksum", gate_exit=0, evidence_text="A0 PASS\n", checksum="absent"),
        coherence_case(fixtures, "failure_pass_no_checksum", gate_exit=9, evidence_text="A0 PASS\n", checksum="absent"),
        coherence_case(fixtures, "failure_negated_pass", gate_exit=9, evidence_text="A0 NOT PASS\n", checksum="absent"),
        coherence_case(fixtures, "failure_pass_substring", gate_exit=9, evidence_text="A0 BYPASS\n", checksum="absent"),
        coherence_case(fixtures, "success_without_pass", gate_exit=0, evidence_text="A0 completed\n", checksum="absent"),
        coherence_case(fixtures, "success_pass_valid_checksum", gate_exit=0, evidence_text="A0 PASS\n", checksum="valid"),
        coherence_case(fixtures, "success_pass_invalid_checksum", gate_exit=0, evidence_text="A0 PASS\n", checksum="invalid"),
    ]


def ordering_observations(fixtures: Path) -> dict[str, Any]:
    root = fixtures / "ordering"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("A0 source\n", encoding="utf-8")
    gate_a0 = "scripts/verify_a0.sh"
    evidence_a0 = "docs/evidence/a0/verification.txt"
    write_gate(root, gate_a0)
    write_evidence(root, evidence_a0, "A0 PASS\n")
    anchor_a0 = commit_all(root, "anchor A0 source and proof")
    state_a0 = state_dict("A0", anchor_a0, gate_a0, evidence_a0, next_milestone="A1")
    write_state(root, state_a0)
    commit_a0 = commit_all(root, "establish A0")
    result_a0 = run_validator(root)

    (root / "source.txt").write_text("A1 source\n", encoding="utf-8")
    gate_a1 = "scripts/verify_a1.sh"
    evidence_a1 = "docs/evidence/a1/verification.txt"
    write_gate(root, gate_a1)
    write_evidence(root, evidence_a1, "A1 PASS\n")
    anchor_a1 = commit_all(root, "anchor A1 source and proof")
    state_a1 = state_dict("A1", anchor_a1, gate_a1, evidence_a1, next_milestone="A2")
    write_state(root, state_a1)
    commit_a1 = commit_all(root, "establish A1")
    result_a1 = run_validator(root)

    write_state(root, state_a0)
    rollback_commit = commit_all(root, "restore older A0 tuple")
    result_rollback = run_validator(root)
    return {
        "sequence": [
            {"state": "A0", "commit": commit_a0, "validator": result_a0},
            {"state": "A1", "commit": commit_a1, "validator": result_a1},
            {"state": "A0_ROLLBACK", "commit": rollback_commit, "validator": result_rollback},
        ],
        "claimed_commits": {"A0": anchor_a0, "A1": anchor_a1},
        "git_log": require(root, "git", "log", "--format=%H %s"),
        "final_state": render_flat_yaml(state_a0),
    }


def recovery_observation(fixtures: Path) -> dict[str, Any]:
    root = fixtures / "recovery"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("A0 source\n", encoding="utf-8")
    gate = "scripts/verify_a0.sh"
    evidence = "docs/evidence/a0/verification.txt"
    write_gate(root, gate)
    write_evidence(root, evidence)
    anchor = commit_all(root, "anchor A0 source and proof")
    valid = state_dict("A0", anchor, gate, evidence)
    write_state(root, valid)
    valid_commit = commit_all(root, "establish valid A0")
    valid_result = run_validator(root)

    partial = dict(valid)
    partial["last_verified_gate"] = "NONE"
    write_state(root, partial)
    partial_commit = commit_all(root, "record invalid partial state")
    partial_result = run_validator(root)

    write_state(root, valid)
    recovered_commit = commit_all(root, "restore valid A0 after invalid state")
    recovered_result = run_validator(root)
    return {
        "sequence": [
            {"state": "VALID_A0", "commit": valid_commit, "validator": valid_result},
            {"state": "INVALID_PARTIAL", "commit": partial_commit, "validator": partial_result},
            {"state": "RESTORED_A0", "commit": recovered_commit, "validator": recovered_result},
        ],
        "recovery_marker_present": False,
        "git_log": require(root, "git", "log", "--format=%H %s"),
    }


def experiment_record(
    identity: str,
    phase: str,
    status: str,
    gate: str,
    evidence: str,
) -> dict[str, Any]:
    return {
        "experiment": {
            "id": identity,
            "title": f"GVI fixture {identity}",
            "phase": phase,
            "status": status,
        },
        "verification": {"gate": gate},
        "outputs": {"evidence": evidence, "tests": []},
    }


def authority_case(
    fixtures: Path,
    identity: str,
    manifest: dict[str, Any],
    *,
    empty_state: bool = False,
) -> dict[str, Any]:
    root = fixtures / f"authority-{identity}"
    root.mkdir()
    init_repo(root)
    (root / "source.txt").write_text("A0 source\n", encoding="utf-8")
    gate = "scripts/verify_a0.sh"
    evidence = "docs/evidence/a0/verification.txt"
    if empty_state:
        anchor = commit_all(root, "source anchor")
        state = state_dict("NONE", "0000000", "NONE", "NONE", phase="A0", next_milestone="A0")
    else:
        write_gate(root, gate)
        write_evidence(root, evidence)
        anchor = commit_all(root, "A0 source and proof anchor")
        state = state_dict("A0", anchor, gate, evidence, next_milestone="A1")
    write_state(root, state)
    manifest_path = root / ".hoa/experiments" / f"{identity}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    commit_all(root, "record canonical state and experiment manifest")
    schema = load_schema(EXPERIMENT_SCHEMA)
    schema_errors = validate_instance(manifest, schema)
    validator = run_validator(root)
    return {
        "id": identity,
        "canonical_state": state,
        "manifest_path": str(manifest_path.relative_to(root)),
        "manifest": manifest,
        "manifest_schema": "ACCEPT" if not schema_errors else "REJECT",
        "manifest_schema_errors": schema_errors,
        "validator": validator,
        "validator_mentions_manifest": "manifest" in (validator["stdout"] + validator["stderr"]).lower()
        or str(manifest_path.relative_to(root)) in validator["stdout"] + validator["stderr"],
    }


def authority_observations(fixtures: Path) -> list[dict[str, Any]]:
    gate_a0 = "scripts/verify_a0.sh"
    evidence_a0 = "docs/evidence/a0/verification.txt"
    return [
        authority_case(
            fixtures,
            "matching_a0",
            experiment_record("A0", "A0", "verified", gate_a0, evidence_a0),
        ),
        authority_case(
            fixtures,
            "contradictory_latest_a1",
            experiment_record("A1", "A1", "verified", "scripts/verify_a1.sh", "docs/evidence/a1/verification.txt"),
        ),
        authority_case(
            fixtures,
            "contradictory_evidence",
            experiment_record("A0", "A0", "verified", gate_a0, "docs/evidence/other/verification.txt"),
        ),
        authority_case(
            fixtures,
            "contradictory_gate",
            experiment_record("A0", "A0", "verified", "scripts/other_gate.sh", evidence_a0),
        ),
        authority_case(
            fixtures,
            "orphan_verified",
            experiment_record("ORPHAN", "Z9", "verified", "scripts/orphan.sh", "docs/evidence/orphan.txt"),
        ),
        authority_case(
            fixtures,
            "empty_with_verified_manifest",
            experiment_record("A0", "A0", "verified", gate_a0, evidence_a0),
            empty_state=True,
        ),
    ]


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    provenance = result["proof_provenance"]
    coherence = result["proof_coherence"]
    authority = result["artifact_authority"]
    return {
        "provenance_acceptances": [
            row["id"] for row in provenance if row["validator"]["classification"] == "ACCEPT"
        ],
        "coherence": {
            row["id"]: row["validator"]["classification"] for row in coherence
        },
        "ordering": {
            row["state"]: row["validator"]["classification"]
            for row in result["history_ordering"]["sequence"]
        },
        "recovery": {
            row["state"]: row["validator"]["classification"]
            for row in result["invalid_state_recovery"]["sequence"]
        },
        "authority": {
            row["id"]: {
                "manifest_schema": row["manifest_schema"],
                "validator": row["validator"]["classification"],
                "validator_mentions_manifest": row["validator_mentions_manifest"],
            }
            for row in authority
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="praxis-gvi-001-") as temporary:
        fixtures = Path(temporary)
        result: dict[str, Any] = {
            "artifact": "praxis-gvi-001-p1-observations/0.1",
            "praxis_p1": require(ROOT, "git", "rev-parse", "main"),
            "instrument": {
                "harness_sha256": sha256_file(INSTRUMENT),
                "validator": str(VALIDATOR),
                "validator_sha256": sha256_file(VALIDATOR),
                "schema_helper_sha256": sha256_file(SCHEMA_HELPER),
                "project_schema_sha256": sha256_file(PROJECT_SCHEMA),
                "experiment_schema_sha256": sha256_file(EXPERIMENT_SCHEMA),
                "platform": os.uname().sysname,
                "python": sys.version.split()[0],
            },
            "proof_provenance": provenance_observations(fixtures),
            "proof_coherence": coherence_observations(fixtures),
            "history_ordering": ordering_observations(fixtures),
            "invalid_state_recovery": recovery_observation(fixtures),
            "artifact_authority": authority_observations(fixtures),
        }
        result["summary"] = summarize(result)

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
