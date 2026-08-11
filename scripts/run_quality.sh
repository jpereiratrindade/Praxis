#!/usr/bin/env bash
set -Eeuo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
"$root/scripts/configure.sh"
"$root/scripts/build.sh"
"$root/scripts/test.sh"
python3 "$root/scripts/validate_governance_repo.py"
PRAXIS_HOME="$root" "$root/build/praxis" doctor
