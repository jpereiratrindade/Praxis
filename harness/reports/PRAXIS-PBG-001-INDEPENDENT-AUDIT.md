# PRAXIS-PBG-001 — Independent candidate audit

## Audit verdict

```text
REJECTED
```

Candidate `1cab1b6e4a62b8ed9ce862eb4320ca94f7af10f3` is not eligible for
adoption review. Its structural tuple model survives exhaustive occupancy and
independent JSON Schema testing, but the complete method does not satisfy the
mission's fail-closed acceptance boundary. Bootstrap handling accepts a current
EMPTY state after a committed partial-history waypoint and does not detect
contradictory verified experiment metadata. The inherited ESTABLISHED path also
accepts mutable or external proof and rollback to an older established tuple.

No semantic repair was made. Fixing experiment-manifest discovery, proof
provenance, gate/evidence coherence, and established-history ordering requires
method-level decisions broader than a focused PRAXIS-PBG-001 implementation
repair.

## Starting state

```text
branch:       feat/bootstrap-state-semantics
candidate:    1cab1b6e4a62b8ed9ce862eb4320ca94f7af10f3
main:         e0532b8f5b9861c3047c0f1ab6173048cb445068
origin/main:  e0532b8f5b9861c3047c0f1ab6173048cb445068
gitlab/main:  e0532b8f5b9861c3047c0f1ab6173048cb445068
working tree: clean before audit artifacts
```

The four candidate commits preserve the advertised chronology: framing,
baseline reproduction, intervention, then candidate report. Recomputed baseline
and candidate classifications match the stored matrices, and all stored
candidate file identities match the current files.

## Candidate claims audited

| Claim | Independent result |
|---|---|
| P1 rejects legitimate empty history | Reproduced |
| Candidate accepts empty history with and without HEAD | Reproduced |
| Candidate accepts anchored SRF P1 read-only | Reproduced |
| All partial tuples fail closed | Contradicted across lifecycle history |
| Git provenance remains distinct from verification | Reproduced for HEAD count, branch, remote, and dirty state |
| Existing established behavior remains accepted | Reproduced, but inherited behavior contains material defects |
| Stored candidate evidence is reproducible | Reproduced for declared matrix and hashes |

## Exhaustive tuple matrix

`S` is both the Praxis helper and independent Draft 2020-12 schema result; the
two implementations agreed on every row. `V` is the candidate validator.

| Pattern | S | V | Semantic classification | Verdict |
|---|---|---|---|---|
| `0000` | ACCEPT | ACCEPT | EMPTY | agree |
| `0001` | REJECT | REJECT | invalid partial | agree |
| `0010` | REJECT | REJECT | invalid partial | agree |
| `0011` | REJECT | REJECT | invalid partial | agree |
| `0100` | REJECT | REJECT | invalid partial | agree |
| `0101` | REJECT | REJECT | invalid partial | agree |
| `0110` | REJECT | REJECT | invalid partial | agree |
| `0111` | REJECT | REJECT | invalid partial | agree |
| `1000` | REJECT | REJECT | invalid partial | agree |
| `1001` | REJECT | REJECT | invalid partial | agree |
| `1010` | REJECT | REJECT | invalid partial | agree |
| `1011` | REJECT | REJECT | invalid partial | agree |
| `1100` | REJECT | REJECT | invalid partial | agree |
| `1101` | REJECT | REJECT | invalid partial | agree |
| `1110` | REJECT | REJECT | invalid partial | agree |
| `1111` | ACCEPT | ACCEPT | structurally established | agree; semantic checks still required |

The current-state atomicity claim is supported: all fourteen partial occupancy
patterns fail at schema and validator. The broader lifecycle claim is not.

## Established-history adversarial cases

| Case | Result | Audit assessment |
|---|---|---|
| Valid tracked fixture | ACCEPT | expected |
| Malformed commit | REJECT | expected |
| Nonexistent commit | REJECT | expected |
| Missing/directory gate | REJECT | expected |
| Missing/directory evidence | REJECT | expected |
| Evidence for another milestone | REJECT | expected |
| Invalid evidence checksum | REJECT | expected |
| Arbitrary zero commit | REJECT | expected |
| Failing gate plus PASS text | ACCEPT | critical counterexample |
| Untracked gate and evidence | ACCEPT | critical counterexample |
| Absolute external gate and evidence | ACCEPT | critical counterexample |
| Milestone inconsistent with phase | ACCEPT | semantic gap |
| Placeholder `UNKNOWN` tuple | ACCEPT | legacy-sentinel ambiguity |

The three critical cases also pass on P1. They are not regressions introduced by
the candidate, but they violate this audit's explicit eligibility condition that
no unresolved counterexample capable of fabricating verification remain.

## Lifecycle matrix

| Transition | Expected | Observed | Verdict |
|---|---|---|---|
| EMPTY → EMPTY | ACCEPT | ACCEPT | pass |
| EMPTY → ESTABLISHED | ACCEPT | ACCEPT | pass |
| ESTABLISHED → ESTABLISHED, forward fixture | ACCEPT | ACCEPT | pass |
| ESTABLISHED → EMPTY | REJECT | REJECT | pass |
| EMPTY → PARTIAL | REJECT | REJECT | pass |
| PARTIAL → ESTABLISHED | REJECT | ACCEPT | fail |
| ESTABLISHED → PARTIAL | REJECT | REJECT | pass |
| PARTIAL → EMPTY | REJECT | ACCEPT | fail |
| later ESTABLISHED → earlier ESTABLISHED | REJECT | ACCEPT | fail |

The candidate only scans predecessors while the current tuple is EMPTY, and
that scan ignores historical PARTIAL states. The established path performs no
transition comparison. Consequently, invalid partial commits can become
lifecycle waypoints and established history can roll back without detection.

## JSON Schema cross-validation

The Praxis helper was compared with Python `jsonschema`'s
`Draft202012Validator` plus `FormatChecker`. There were zero disagreements over
the sixteen project-state occupancy patterns and eight focused cases exercising:

- exactly one, zero, and multiple `oneOf` matches;
- `not` success and failure;
- the nested object shape used by the Praxis contract;
- a malformed data type.

No pre-existing Praxis contract other than `project-state.schema.json` uses
`oneOf` or `not`, so no unrelated helper-semantic regression was found.

## Fail-closed attacks and cross-artifact consistency

The candidate accepts an exact EMPTY canonical state together with an
individually schema-valid experiment record whose status is `verified`. It also
accepts established A0 while a verified A1 experiment record is present. The
method has no governed discovery rule connecting experiment records to project
state, although the policy requires canonical state and manifests to remain
consistent. This prevents a focused implementation-only repair.

EMPTY remains independent of whether the repository has zero or multiple
commits, its branch name, remote configuration, or an unrelated dirty file. A
non-Git directory is rejected, consistent with the method's dependence on Git
provenance but distinct from whether HEAD exists.

Legacy `null`, empty string, missing field, lowercase `none` paired with the
zero-commit sentinel, and arbitrary zero-commit variants fail closed. A fully
populated placeholder tuple such as `UNKNOWN` is treated as ESTABLISHED and can
pass when matching files and text exist.

## Hypothesis re-evaluation

### PBG-H01 — SUPPORTED

Legitimate projects with no verified milestone are evidenced by SRF P1 and by
controlled repositories before and after their first provenance commit. The
candidate accepts them. This support is ontological and empirical, not inferred
solely from candidate behavior.

### PBG-H02 — SUPPORTED

At P1, Cases A, B, and SRF all fail because `NONE` is interpreted as a gate
path. The representation gap is independently reproduced.

### PBG-H03 — CONTRADICTED

All current-state partial tuples fail, but committed partial predecessors can
transition to EMPTY or ESTABLISHED and validate. EMPTY can also coexist with a
verified experiment record. Bootstrap support therefore weakens fail-closed
project-level behavior.

### PBG-H04 — SUPPORTED

EMPTY validation is invariant under zero versus multiple commits, main versus
feature branch, remote presence, and an unrelated dirty file. SRF remains a
committed but scientifically unverified example.

### PBG-H05 — INCONCLUSIVE

Praxis and the ordinary established fixture continue to pass, so there is no
observed regression in those examples. However, inherited ESTABLISHED
validation accepts mutable/external proof and rollback, and no additional
readily discoverable established governed project was available. The stronger
no-semantic-regression claim is not established.

## Unexpected observations

1. The stored candidate matrix is reproducible but materially incomplete: it
   covers four of fourteen partial occupancy patterns and no historical partial
   transitions.
2. `PARTIAL → EMPTY` is rejected at P1 only incidentally because P1 interprets
   `NONE` as a missing path; the candidate changes it to acceptance without
   recognizing the partial predecessor.
3. Candidate and P1 both accept untracked, absolute external, or gate-inconsistent
   established proof.
4. No JSON Schema helper disagreement was found.

## Candidate modifications during audit

```text
semantic repair: none
counterexamples: preserved in executable audit generator and machine-readable result
```

The audit added only an independent generator, evidence, and this report. It did
not modify schema, validator, lifecycle, template, policy, or candidate claims.

## Regression results

```text
CTest:                 PASS (5/5)
Praxis quality:        PASS
Praxis self-governance: PASS
methodology schema:    PASS
candidate matrix:      PASS / matches stored classifications
SRF P1 read-only:      ACCEPT by candidate
```

SRF remained clean on `main` at
`3b5615e5b5302ca93dc56085a999527a8206339e`; local, GitHub, and GitLab refs are
equal. RF-A0 remains active, unverified, and unpromoted with RF-A1 unauthorized.
The read-only ledger verifier reports five runs and head
`c97bdd0e12e4f7c2295739fb52e4a46f0b7c2b081909570fbb999375de8919e5`.

No other Praxis-governed project was found in the readily discoverable local C++
workspace, so no additional external established-project regression was used.

## Final candidate state and limits

The candidate correctly introduces a useful current-state EMPTY/ESTABLISHED
structural distinction. It does not establish safe historical transitions,
cross-artifact consistency, proof provenance, gate/evidence coherence,
established-history monotonicity, adoption, or promotion.

```text
branch: feat/bootstrap-state-semantics
main modified: no
push performed: no
merge performed: no
promotion performed: no
SRF modified: no
```
