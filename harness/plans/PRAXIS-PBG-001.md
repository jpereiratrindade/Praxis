# PRAXIS-PBG-001 — Bootstrap-state semantics investigation

## Authority and boundary

```text
status: active investigation
baseline: e0532b8f5b9861c3047c0f1ab6173048cb445068
branch: feat/bootstrap-state-semantics
adoption: none
promotion: none
```

SRF P1 is read-only external evidence anchored at
`3b5615e5b5302ca93dc56085a999527a8206339e`. This investigation may create a
Praxis candidate on its dedicated branch. It must not modify SRF, rewrite H06,
merge to Praxis `main`, or promote a method revision.

## Observed starting condition

The current project-state schema accepts the exact tuple used for honest empty
verification history:

```text
last_verified_milestone: NONE
last_verified_commit: 0000000
last_verified_gate: NONE
last_verified_evidence: NONE
```

The P1 validator then interprets `NONE` as a filesystem path and fails at
`gate missing — NONE`. The method and policy do not currently define whether
the four values form one atomic lifecycle state.

## Pre-implementation hypotheses

### PBG-H01

A governed project can validly exist while verified history is empty, with or
without a Git commit.

### PBG-H02

Praxis P1 does not represent that state coherently through the combined schema,
validator, lifecycle rules, and documentation.

### PBG-H03

Treating the exact empty-history tuple as one atomic canonical state can accept
legitimate bootstrap projects while continuing to reject every partially
populated verification tuple.

### PBG-H04

Git provenance and scientific verification can remain independent: both an
uncommitted project and a committed project may have empty verified history.

### PBG-H05

The correction can preserve Praxis self-governance and ordinary established
verification histories without changing their meaning.

## Controlled cases and predictions

| Case | State | P1 prediction | Candidate prediction |
|---|---|---|---|
| A | new Git repository, no commit, exact empty tuple | reject at missing `NONE` path | accept |
| B | committed repository, exact empty tuple | reject at missing `NONE` path | accept |
| C | first established verification with real gate/evidence/ancestor | accept | accept |
| D1 | milestone claimed, remaining tuple empty | reject | reject as partial tuple |
| D2 | commit claimed, remaining tuple empty | reject | reject as partial tuple |
| D3 | gate claimed, remaining tuple empty | reject | reject as partial tuple |
| D4 | evidence claimed, remaining tuple empty | reject | reject as partial tuple |
| D5 | return from established history to empty tuple | P1 reason unspecified | reject as non-monotonic |
| E | existing verified Praxis state | accept | accept |
| F | anchored SRF P1, exact empty tuple | reject at missing `NONE` path | accept read-only |

## Comparison rules

- `SUPPORTED`: the declared cases produce all predicted classifications and the
  cited artifacts preserve the observed outputs.
- `CONTRADICTED`: a valid case has the opposite classification, an invalid
  partial history passes, or an established history regresses.
- `INCONCLUSIVE`: test construction, Git state, or instrumentation prevents the
  result from being attributed to the state semantics.

Each hypothesis is compared only against its declared cases; overall test PASS
does not automatically support every hypothesis.

## Candidate correction boundary

The smallest candidate under test is:

1. define the exact four-value tuple as the canonical empty-history state;
2. require all four values to be empty or all four to describe established
   verification;
3. skip gate, evidence, checksum, and ancestry checks only for the exact empty
   tuple;
4. reject a transition from committed established history back to empty;
5. preserve all existing checks for established history.

The investigation may revise or reject this candidate if controlled evidence
contradicts it. The tuple is not an unrestricted bypass and does not confer
verification or promotion.

## Expected evidence

- baseline and candidate validator identities;
- machine-readable results for A–F;
- raw validator output per case;
- Praxis quality and self-governance output;
- read-only SRF P1 output and identity;
- unexpected observations and hypothesis comparisons;
- candidate learning explicitly marked as non-adopted.
