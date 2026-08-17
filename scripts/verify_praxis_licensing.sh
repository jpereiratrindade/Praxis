#!/usr/bin/env bash
set -Eeuo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

echo "=== Praxis PRAXIS-LIC-001 — Governed Project Licensing ==="
python3 -m unittest -v tests/licensing/test_governed_licensing.py
python3 scripts/validate_methodology_repo.py
python3 scripts/validate_governed_project.py .

expected="3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"
observed="$(sha256sum LICENSE | awk '{print $1}')"
test "$observed" = "$expected"
grep -Fq "SPDX-License-Identifier: GPL-3.0-only" README.md
test ! -e .hoa/licensing.yaml
echo "PASS Praxis self-license preserved — GPL-3.0-only ($observed)"
(cd docs/methodology/evidence/praxis-lic-001 && sha256sum --check verification.sha256)
echo
echo "Praxis PRAXIS-LIC-001: PASS"
