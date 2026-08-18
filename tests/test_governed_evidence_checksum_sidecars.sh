#!/usr/bin/env bash
set -Eeuo pipefail

PRAXIS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATOR="$PRAXIS_ROOT/scripts/validate_governed_project.py"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p \
    "$TMP/.hoa" \
    "$TMP/scripts" \
    "$TMP/docs/evidence"

cat > "$TMP/scripts/gate.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$TMP/scripts/gate.sh"

cat > "$TMP/scripts/bootstrap_project.sh" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$TMP/scripts/bootstrap_project.sh"

printf '%s\n' 'MVP-0: PASS' \
    > "$TMP/docs/evidence/verification.txt"

HASH="$(
    sha256sum "$TMP/docs/evidence/verification.txt" |
    awk '{print $1}'
)"

printf '%s  %s\n' \
    "$HASH" \
    'docs/evidence/verification.txt' \
    > "$TMP/docs/evidence/verification.txt.sha256"

git -C "$TMP" init -q -b main
git -C "$TMP" config user.name "Praxis Regression"
git -C "$TMP" config user.email "praxis-regression@example.invalid"

git -C "$TMP" add scripts docs
git -C "$TMP" commit -q -m "fixture: governed evidence"

BASE="$(git -C "$TMP" rev-parse HEAD)"

cat > "$TMP/.hoa/project-state.yaml" <<EOF
version: "1.0"
project: praxis_checksum_regression
governance_method: praxis-governed-engineering/0.1
bootstrap_script: scripts/bootstrap_project.sh
bootstrap_policy: create_once
phase: MVP-0
status: active
last_verified_milestone: MVP-0
last_verified_commit: "$BASE"
last_verified_gate: scripts/gate.sh
last_verified_evidence: docs/evidence/verification.txt
next_milestone: NEXT
next_milestone_status: proposed
next_milestone_authorized: false
updated_on: "2026-08-18"
readiness_principle: evidence_before_score
EOF

git -C "$TMP" add .hoa/project-state.yaml
git -C "$TMP" commit -q -m "fixture: project state"

run_validator() {
    python3 "$VALIDATOR" "$TMP" 2>&1
}

echo "CASE 1 canonical verification.txt.sha256"

OUT="$(run_validator)"
printf '%s\n' "$OUT"

grep -q 'governed evidence checksum' <<<"$OUT"

echo
echo "CASE 2 canonical sidecar corruption must fail"

printf '%064d  docs/evidence/verification.txt\n' 0 \
    > "$TMP/docs/evidence/verification.txt.sha256"

if run_validator >/tmp/praxis-checksum-bad.out 2>&1; then
    echo "FAIL: corrupted checksum was accepted"
    exit 20
fi

grep -q 'governed evidence checksum' \
    /tmp/praxis-checksum-bad.out

echo "PASS: corruption rejected"

echo
echo "CASE 3 legacy verification.sha256 remains supported"

rm "$TMP/docs/evidence/verification.txt.sha256"

printf '%s  %s\n' \
    "$HASH" \
    'docs/evidence/verification.txt' \
    > "$TMP/docs/evidence/verification.sha256"

OUT="$(run_validator)"
printf '%s\n' "$OUT"

grep -q 'governed evidence checksum' <<<"$OUT"

echo
echo "CASE 4 disagreeing sidecars must fail"

printf '%s  %s\n' \
    "$HASH" \
    'docs/evidence/verification.txt' \
    > "$TMP/docs/evidence/verification.txt.sha256"

printf '%064d  docs/evidence/verification.txt\n' 0 \
    > "$TMP/docs/evidence/verification.sha256"

if run_validator >/tmp/praxis-checksum-disagree.out 2>&1; then
    echo "FAIL: disagreeing checksum sidecars were accepted"
    exit 21
fi

grep -q 'sidecars disagree' \
    /tmp/praxis-checksum-disagree.out

echo "PASS: disagreement rejected"

echo
echo "CHECKSUM SIDECAR REGRESSION: PASS"
