#!/usr/bin/env python3
"""Praxis Governed Engineering Method 0.1 — validador genérico."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from governed_method_schema import load_flat_yaml, load_schema, validate_instance


PRAXIS_ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS  {message}")


def run(root: Path, *cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=root, text=True, capture_output=True, check=False
    )


parser = argparse.ArgumentParser()
parser.add_argument("workspace", nargs="?", default=".")
args = parser.parse_args()

root = Path(args.workspace).resolve()
state_path = root / ".hoa/project-state.yaml"
schema_path = PRAXIS_ROOT / "contracts/methodology/project-state.schema.json"

if not state_path.is_file():
    fail("canonical state — .hoa/project-state.yaml")
ok("canonical state — .hoa/project-state.yaml")

try:
    state = load_flat_yaml(state_path)
    schema = load_schema(schema_path)
except Exception as exc:
    fail(f"canonical state/schema parse — {exc}")

schema_errors = validate_instance(state, schema)
if schema_errors:
    for error in schema_errors:
        print(f"FAIL  canonical state schema — {error}", file=sys.stderr)
    raise SystemExit(1)
ok("canonical state conforms to project-state.schema.json")

method = state["governance_method"]
ok(f"governance method — {method}")

milestone = state["last_verified_milestone"]
commit = state["last_verified_commit"]
gate = state["last_verified_gate"]
evidence = state["last_verified_evidence"]
next_status = state["next_milestone_status"]
next_authorized = state["next_milestone_authorized"]

for label, rel in (("gate", gate), ("governed evidence", evidence)):
    if not (root / rel).is_file():
        fail(f"{label} missing — {rel}")
    ok(f"{label} — {rel}")

text = (root / evidence).read_text(encoding="utf-8", errors="replace")
if not re.search(
    rf"{re.escape(milestone)}.*PASS|PASS.*{re.escape(milestone)}", text
):
    fail(f"governed evidence does not prove PASS — {milestone}")
ok(f"governed evidence proves PASS — {milestone}")

checksum = (root / evidence).with_suffix(".sha256")
if checksum.is_file():
    expected = checksum.read_text(encoding="utf-8").split()[0]
    observed = hashlib.sha256((root / evidence).read_bytes()).hexdigest()
    if expected != observed:
        fail("governed evidence checksum")
    ok("governed evidence checksum")

ancestor = run(root, "git", "merge-base", "--is-ancestor", commit, "HEAD")
if ancestor.returncode != 0:
    fail(f"verified commit is not ancestor of HEAD — {commit}")
ok(f"verified commit ancestry — {commit}")

for transient in (".build", "build"):
    path = root / transient
    if path.exists():
        tracked = run(root, "git", "ls-files", transient)
        if tracked.stdout.strip():
            fail(f"transient build is tracked — {transient}")

        ignored = run(root, "git", "check-ignore", transient)
        if ignored.returncode == 0:
            ok(f"transient build ignored — {transient}")
        else:
            fail(f"transient build exists but is not ignored — {transient}")

if next_status == "proposed" and next_authorized is not False:
    fail("proposed next milestone must not be implicitly authorized")
ok("next milestone authorization explicit")

bootstrap_policy = state.get("bootstrap_policy")
if bootstrap_policy:
    ok(f"bootstrap policy — {bootstrap_policy}")

bootstrap_script = state.get("bootstrap_script")
if bootstrap_script:
    if not (root / bootstrap_script).is_file():
        fail(f"bootstrap script missing — {bootstrap_script}")
    ok(f"bootstrap script — {bootstrap_script}")

print("\nGoverned project method v0.1: READY")
