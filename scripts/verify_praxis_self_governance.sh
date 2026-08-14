#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "=== Praxis PRAXIS-SG-001 — Self-Governance v0.1 ==="
echo "root=$ROOT"
echo

echo "=== quality ==="
./scripts/run_quality.sh

echo
echo "=== workspace governance ==="
./scripts/validate_workspace_governance.py

echo
echo "=== governed-project self validation ==="
./scripts/validate_governed_project.py .

echo
echo "[PASS] Praxis aplica a si próprio o estado canônico do método v0.1"
echo
echo "Praxis PRAXIS-SG-001: PASS"
