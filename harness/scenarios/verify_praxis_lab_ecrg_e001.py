#!/usr/bin/env python3
"""Verificador local e não destrutivo de PRAXIS-LAB-ECRG-E001."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "harness/scenarios/PRAXIS-LAB-ECRG-E001.json"
REPORT = ROOT / "harness/reports/PRAXIS-LAB-ECRG-E001.md"
SCHEMA = ROOT / "contracts/methodology/experiment-record.schema.json"

ALLOWED_CHANGES = {
    "harness/scenarios/PRAXIS-LAB-ECRG-E001.json",
    "harness/scenarios/verify_praxis_lab_ecrg_e001.py",
    "harness/reports/PRAXIS-LAB-ECRG-E001.md",
    "harness/evidence/PRAXIS-LAB-ECRG-E001-verification.txt",
    "harness/evidence/PRAXIS-LAB-ECRG-E001-verification.sha256",
}

REQUIRED_CLASSES = {
    "OBSERVATION",
    "FINDING",
    "INTERPRETATION",
    "MRE_CANDIDATE",
    "MOG_CLAIM",
    "NORMATIVE_PROPOSAL",
    "EXPERIMENTAL_HYPOTHESIS",
    "AUTHORIZED_ACTION",
    "NOT_AUTHORIZED",
}

REQUIRED_INVARIANTS = {f"ECRG1-I{number:02d}" for number in range(1, 9)}


def fail(message: str) -> None:
    print(f"FAIL  {message}")
    raise SystemExit(1)


def passed(message: str) -> None:
    print(f"PASS  {message}")


def run_git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def changed_paths() -> set[str]:
    result = run_git("status", "--porcelain", "--untracked-files=all")
    if result.returncode != 0:
        fail("git status executable")

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.add(raw)
    return paths


def verify_schema(record: dict[str, Any]) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from governed_method_schema import validate_instance

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = validate_instance(record, schema)
    if errors:
        fail("experiment record schema — " + "; ".join(errors))
    passed("experiment record conforms to experiment-record.schema.json")


def verify_inputs(record: dict[str, Any]) -> None:
    for item in record["experiment"]["inputs"]:
        path = Path(item["path"])
        if not path.is_file():
            fail(f"input missing — {path}")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != item["sha256"]:
            fail(f"input digest — {item['role']}")
        passed(f"input digest — {item['role']}")


def main() -> int:
    print("PRAXIS-LAB-ECRG-E001 — local constitution verifier")
    print("command=python3 harness/scenarios/verify_praxis_lab_ecrg_e001.py")
    print(f"timestamp={dt.datetime.now(dt.timezone.utc).isoformat()}")
    print(f"root={ROOT}")

    if not RECORD.is_file() or not REPORT.is_file() or not SCHEMA.is_file():
        fail("declared internal input files exist")
    passed("declared internal input files exist")

    record = json.loads(RECORD.read_text(encoding="utf-8"))
    verify_schema(record)

    experiment = record["experiment"]
    if experiment.get("id") != "PRAXIS-LAB-ECRG-E001":
        fail("experiment identity")
    passed("experiment identity")

    if experiment.get("status") != "proposed":
        fail("experiment remains proposed")
    passed("experiment remains proposed")

    invariant_ids = {item.get("id") for item in experiment.get("invariants", [])}
    if invariant_ids != REQUIRED_INVARIANTS:
        fail("ECRG-E001 invariant set")
    passed("ECRG-E001 invariant set")

    classifications = record.get("epistemic_classification", [])
    observed_classes = {item.get("class") for item in classifications}
    if observed_classes != REQUIRED_CLASSES:
        fail("epistemic classification set")
    passed("epistemic classification set")

    finding = next(item for item in classifications if item["class"] == "FINDING")
    authorization = next(
        item for item in classifications if item["class"] == "AUTHORIZED_ACTION"
    )
    if finding.get("can_alter_state") is not False:
        fail("finding does not authorize state change")
    if authorization.get("state_scope") != "experimental_harness_only":
        fail("authorized action remains confined")
    passed("finding and authorization remain distinct")

    if record.get("relation_to_mog", {}).get("canonical_state_change") is not False:
        fail("MOG canonical state remains unchanged")
    if record.get("relation_to_mre", {}).get("authority") != "epistemic_candidate_only":
        fail("MRE remains epistemic candidate")
    passed("MRE and MOG remain distinct")

    if (
        record.get("relation_to_sg_002", {}).get("disposition")
        != "independent_candidate_not_implemented"
    ):
        fail("PRAXIS-SG-002 remains independent and unimplemented")
    passed("PRAXIS-SG-002 remains independent and unimplemented")

    verify_inputs(record)

    baseline = experiment["baseline"]["commit"]
    ancestry = run_git("merge-base", "--is-ancestor", baseline, "HEAD")
    if ancestry.returncode != 0:
        fail("baseline commit is ancestor of HEAD")
    passed("baseline commit is ancestor of HEAD")

    changes = changed_paths()
    unexpected = changes - ALLOWED_CHANGES
    if unexpected:
        fail("unexpected working-tree changes — " + ", ".join(sorted(unexpected)))
    if not {
        "harness/scenarios/PRAXIS-LAB-ECRG-E001.json",
        "harness/scenarios/verify_praxis_lab_ecrg_e001.py",
        "harness/reports/PRAXIS-LAB-ECRG-E001.md",
    }.issubset(changes):
        fail("minimum experimental artifacts are visible in working tree")
    passed("working tree is confined to authorized experimental artifacts")

    print("files_considered=")
    for path in sorted(changes):
        print(f"- {path}")

    print("result=PASS")
    print("claim_boundary=experiment constitution only; ECRG and SG-002 not promoted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
