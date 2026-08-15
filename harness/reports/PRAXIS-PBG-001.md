# PRAXIS-PBG-001 — Candidate bootstrap-state result

## Status

```text
candidate: implemented on feat/bootstrap-state-semantics
adoption: none
promotion: none
main merge: not performed
remote push: not performed
```

The candidate was evaluated against Praxis baseline
`e0532b8f5b9861c3047c0f1ab6173048cb445068` and read-only SRF P1
`3b5615e5b5302ca93dc56085a999527a8206339e`.

## Baseline reproduction

Praxis P1 accepted the sentinel values structurally but rejected both an
uncommitted and a committed empty-history project at `gate missing — NONE`.
The anchored SRF P1 failed at the same point. Complete established fixtures and
Praxis self-governance passed.

Partial tuples also failed under P1, but only as incidental missing paths; the
schema and method did not state an atomic empty/established invariant or a
monotonic lifecycle transition.

## Root cause

The defect crossed five aligned surfaces:

1. ontology lacked explicit `empty | established` history states;
2. schema validated fields independently rather than as one tuple;
3. validator interpreted every gate/evidence value as an established path;
4. lifecycle did not reject a return from established history to empty;
5. policy, method text, and scaffold template did not agree on bootstrap.

## Candidate correction

The candidate defines:

```text
empty       = NONE / 0000000 / NONE / NONE
established = milestone / commit / gate / evidence
```

The schema expresses the alternatives with `oneOf`; its internal helper now
executes `oneOf` and `not`. The validator skips established-history reference
checks only for the exact empty tuple and rejects an empty tuple if established
state exists in the current Git history. The scaffold, policy, and method text
use the same ontology.

No project-name exception exists. A commit may anchor provenance while verified
history remains empty.

## Outcomes

| Case | Candidate outcome |
|---|---|
| A — uncommitted empty history | ACCEPT |
| B — committed empty history | ACCEPT |
| C — established history | ACCEPT |
| D1–D4 — partial tuple | REJECT at schema |
| D5 — established-to-empty regression | REJECT at lifecycle |
| E — Praxis established history | ACCEPT |
| F — anchored SRF P1 | ACCEPT read-only |

All PBG-H01 through PBG-H05 are `SUPPORTED` within this matrix. The mappings to
individual cases and raw outputs are preserved in
`harness/evidence/praxis-pbg-001/result.json`.

## Regression and boundary

- candidate matrix: PASS;
- CTest: 5/5 PASS;
- Praxis quality: PASS;
- Praxis self-governance: PASS;
- standard Draft 2020-12 schema parity: PASS;
- SRF local/GitHub/GitLab identity remained equal and SRF stayed clean.

No additional unexpected observation occurred. The candidate does not establish
cross-branch lifecycle monotonicity, method adoption, migration policy for
noncanonical legacy sentinels, or scientific verification of any bootstrap
project. Those remain outside this candidate's evidence.
