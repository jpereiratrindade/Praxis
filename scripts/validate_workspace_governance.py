#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "include/sister/hoa/ProjectWorkspace.hpp",
    "include/sister/hoa/GitSyncStatus.hpp",
    "docs/adr/ADR-0004-workspace-as-operational-boundary.md",
    "docs/engineering/WORKSPACE_ENGINEERING.md",
    "policies/workspace_authority_policy.md",
    "contracts/workspace/project-workspace.schema.json",
    "harness/skills/workspace.inspect.yaml",
    "harness/skills/workspace.sync-status.yaml",
    "harness/scenarios/HOA-EXP-004-generic-cpp-workspace.md",
]
missing = [item for item in required if not (root / item).is_file()]
for item in required:
    print(("PASS" if item not in missing else "FAIL"), item)
if missing:
    print(f"Workspace governance: NOT_READY ({len(missing)} missing)")
    sys.exit(4)
print("Workspace governance: READY")
