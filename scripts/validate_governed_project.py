#!/usr/bin/env python3
"""Praxis Governed Engineering Method 0.1 — validador genérico."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from governed_method_schema import (
    load_flat_yaml,
    load_schema,
    parse_scalar,
    validate_instance,
)


PRAXIS_ROOT = Path(__file__).resolve().parents[1]
EMPTY_HISTORY = {
    "last_verified_milestone": "NONE",
    "last_verified_commit": "0000000",
    "last_verified_gate": "NONE",
    "last_verified_evidence": "NONE",
}


def fail(message: str) -> None:
    print(f"FAIL  {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS  {message}")


def run(root: Path, *cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=root, text=True, capture_output=True, check=False
    )


def verification_history_state(state: dict[str, object]) -> str:
    empty_fields = [state.get(key) == value for key, value in EMPTY_HISTORY.items()]
    if all(empty_fields):
        return "empty"
    if any(empty_fields):
        return "partial"
    return "established"


def state_from_git_text(text: str) -> dict[str, object]:
    state: dict[str, object] = {}
    for original in text.splitlines():
        line = original.strip()
        if not line or line.startswith("#") or ":" not in original:
            continue
        key, raw = original.split(":", 1)
        state[key.strip()] = parse_scalar(raw)
    return state


def has_established_predecessor(root: Path) -> bool:
    inside = run(root, "git", "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        fail("Git repository missing for empty verification history")

    head = run(root, "git", "rev-parse", "--verify", "HEAD")
    if head.returncode != 0:
        return False

    history = run(
        root,
        "git",
        "log",
        "--format=%H",
        "--",
        ".hoa/project-state.yaml",
    )
    if history.returncode != 0:
        fail("cannot inspect verification-history transitions")
    for revision in history.stdout.splitlines():
        snapshot = run(root, "git", "show", f"{revision}:.hoa/project-state.yaml")
        if snapshot.returncode != 0:
            fail(f"cannot inspect canonical state at {revision}")
        if verification_history_state(state_from_git_text(snapshot.stdout)) == "established":
            return True
    return False


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

history_state = verification_history_state(state)
if history_state == "partial":
    fail("partial verification history — expected exact empty or complete established tuple")
ok(f"verification history state — {history_state}")

if history_state == "empty":
    if has_established_predecessor(root):
        fail("verification history cannot regress from established to empty")
    ok("empty verification history has no established predecessor")
else:
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
