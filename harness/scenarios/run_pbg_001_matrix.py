#!/usr/bin/env python3
"""Controlled bootstrap-state matrix for PRAXIS-PBG-001."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EMPTY_HISTORY = {
    "last_verified_milestone": "NONE",
    "last_verified_commit": "0000000",
    "last_verified_gate": "NONE",
    "last_verified_evidence": "NONE",
}


def command(root: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def require_command(root: Path, *argv: str) -> str:
    result = command(root, *argv)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed in {root}: {argv!r}\n{result.stdout}{result.stderr}"
        )
    return result.stdout.strip()


def state_text(project: str, overrides: dict[str, Any] | None = None) -> str:
    state: dict[str, Any] = {
        "version": "1.0",
        "project": project,
        "governance_method": "praxis-governed-engineering/0.1",
        "phase": "A0",
        "status": "active",
        **EMPTY_HISTORY,
        "next_milestone": "A0",
        "next_milestone_status": "active",
        "next_milestone_authorized": True,
        "updated_on": "2026-08-15",
    }
    state.update(overrides or {})
    lines = []
    for key, value in state.items():
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif key in {"version", "last_verified_commit"}:
            rendered = json.dumps(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "\n".join(lines) + "\n"


def initialize(root: Path, project: str, overrides: dict[str, Any] | None = None) -> None:
    require_command(root, "git", "init", "-b", "main")
    require_command(root, "git", "config", "user.name", "Praxis PBG Fixture")
    require_command(root, "git", "config", "user.email", "pbg-fixture@invalid")
    (root / ".hoa").mkdir()
    (root / ".hoa/project-state.yaml").write_text(
        state_text(project, overrides), encoding="utf-8"
    )


def commit_all(root: Path, message: str) -> str:
    require_command(root, "git", "add", "-A")
    require_command(root, "git", "commit", "-m", message)
    return require_command(root, "git", "rev-parse", "HEAD")


def make_established(root: Path, project: str) -> str:
    initialize(root, project)
    gate = root / "scripts/verify_a0.sh"
    evidence = root / "docs/evidence/a0/verification.txt"
    gate.parent.mkdir(parents=True)
    evidence.parent.mkdir(parents=True)
    gate.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    evidence.write_text("A0 PASS\n", encoding="utf-8")
    evidence.with_suffix(".sha256").write_text(
        hashlib.sha256(evidence.read_bytes()).hexdigest() + "  verification.txt\n",
        encoding="utf-8",
    )
    anchor = commit_all(root, "anchor fixture evidence")
    (root / ".hoa/project-state.yaml").write_text(
        state_text(
            project,
            {
                "last_verified_milestone": "A0",
                "last_verified_commit": anchor,
                "last_verified_gate": "scripts/verify_a0.sh",
                "last_verified_evidence": "docs/evidence/a0/verification.txt",
                "next_milestone": "A1",
                "next_milestone_status": "proposed",
                "next_milestone_authorized": False,
            },
        ),
        encoding="utf-8",
    )
    commit_all(root, "record established verification")
    return anchor


def execute_case(
    identity: str,
    description: str,
    root: Path,
    validator: Path,
    expected_accept: bool,
    output: Path,
) -> dict[str, Any]:
    result = command(root, sys.executable, str(validator), str(root))
    accepted = result.returncode == 0
    raw_name = f"case-{identity.lower()}-validator.txt"
    (output / raw_name).write_text(
        f"exit_status={result.returncode}\n\nSTDOUT\n{result.stdout}\nSTDERR\n{result.stderr}",
        encoding="utf-8",
    )
    return {
        "id": identity,
        "description": description,
        "expected": "ACCEPT" if expected_accept else "REJECT",
        "observed": "ACCEPT" if accepted else "REJECT",
        "exit_status": result.returncode,
        "matches_prediction": accepted == expected_accept,
        "raw_evidence": raw_name,
    }


def expected(phase: str, identity: str) -> bool:
    if identity in {"C", "E"}:
        return True
    if identity in {"A", "B", "F"}:
        return phase == "candidate"
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["baseline", "candidate"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validator", type=Path, default=ROOT / "scripts/validate_governed_project.py")
    parser.add_argument("--external-srf", type=Path)
    args = parser.parse_args()

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    validator = args.validator.resolve()
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="praxis-pbg-001-") as temporary:
        fixtures = Path(temporary)

        case_a = fixtures / "case-a"
        case_a.mkdir()
        initialize(case_a, "case-a-empty-uncommitted")

        case_b = fixtures / "case-b"
        case_b.mkdir()
        initialize(case_b, "case-b-empty-committed")
        commit_all(case_b, "anchor empty history")

        case_c = fixtures / "case-c"
        case_c.mkdir()
        make_established(case_c, "case-c-established")

        partials = {
            "D1": {"last_verified_milestone": "A0"},
            "D2": {"last_verified_commit": "1234567"},
            "D3": {"last_verified_gate": "scripts/verify_a0.sh"},
            "D4": {"last_verified_evidence": "docs/evidence/a0/verification.txt"},
        }
        partial_roots: dict[str, Path] = {}
        for identity, overrides in partials.items():
            case_root = fixtures / f"case-{identity.lower()}"
            case_root.mkdir()
            initialize(case_root, f"case-{identity.lower()}-partial", overrides)
            partial_roots[identity] = case_root

        case_d5 = fixtures / "case-d5"
        case_d5.mkdir()
        make_established(case_d5, "case-d5-regression")
        (case_d5 / ".hoa/project-state.yaml").write_text(
            state_text("case-d5-regression"), encoding="utf-8"
        )
        commit_all(case_d5, "attempt regression to empty history")

        controlled = [
            ("A", "uncommitted repository with exact empty-history tuple", case_a),
            ("B", "committed repository with exact empty-history tuple", case_b),
            ("C", "established verification with complete references", case_c),
            ("D1", "partial tuple: milestone only", partial_roots["D1"]),
            ("D2", "partial tuple: commit only", partial_roots["D2"]),
            ("D3", "partial tuple: gate only", partial_roots["D3"]),
            ("D4", "partial tuple: evidence only", partial_roots["D4"]),
            ("D5", "committed regression from established to empty history", case_d5),
        ]
        for identity, description, case_root in controlled:
            results.append(
                execute_case(
                    identity,
                    description,
                    case_root,
                    validator,
                    expected(args.phase, identity),
                    output,
                )
            )

    results.append(
        execute_case(
            "E",
            "existing verified Praxis repository",
            ROOT,
            validator,
            expected(args.phase, "E"),
            output,
        )
    )
    if args.external_srf:
        results.append(
            execute_case(
                "F",
                "anchored SRF P1 with exact empty-history tuple",
                args.external_srf.resolve(),
                validator,
                expected(args.phase, "F"),
                output,
            )
        )

    matrix = {
        "artifact": "praxis-pbg-001-bootstrap-matrix/0.1",
        "phase": args.phase,
        "validator": str(validator),
        "validator_sha256": hashlib.sha256(validator.read_bytes()).hexdigest(),
        "results": results,
        "all_predictions_matched": all(item["matches_prediction"] for item in results),
    }
    (output / "matrix.json").write_text(
        json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for item in results:
        print(
            f"{'PASS' if item['matches_prediction'] else 'FAIL'} {item['id']} "
            f"expected={item['expected']} observed={item['observed']}"
        )
    return 0 if matrix["all_predictions_matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
