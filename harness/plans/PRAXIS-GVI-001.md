# PRAXIS-GVI-001 — Governed verification integrity protocol

## Authority and historical boundary

```text
investigation: PRAXIS-GVI-001
status: prediction-first investigation
authoritative baseline: e0532b8f5b9861c3047c0f1ab6173048cb445068
rejected PBG evidence: 8f9b685c63617abb7eb02f574d0a74642c1f665d
SRF read-only reference: 3b5615e5b5302ca93dc56085a999527a8206339e
adoption authority: none
merge authority: none
promotion authority: none
```

This protocol precedes the decisive GVI observations. It investigates what
Praxis P1 actually establishes when it accepts governed verification. It does
not assume the rejected PBG ontology and does not authorize a production fix.

## Question

What minimum executable properties must hold before Praxis may truthfully
accept a claim that a project state is governed and verified?

## Interpretation boundary

An observation establishes only the behavior of the identified validator,
schema, fixture, repository history, and artifacts. Acceptance by the validator
does not independently establish scientific truth. Candidate invariants are
learning proposals, not adopted Praxis rules.

## Hypotheses and predictions

### GVI-H01 — Provenance weakness

**Hypothesis:** P1 can accept verification without proving that gate and
evidence belong to the governed source state.

**Prediction:** otherwise-valid tuples using untracked proof, repository-external
proof, or proof absent from the claimed commit will be accepted.

**Falsification:** P1 rejects every such case because it establishes repository
containment, Git tracking, and historical presence of the exact proof bytes.

**Observation:** generate isolated Git repositories and invoke the exact P1
validator. Record path containment, `git ls-files`, and `git cat-file` facts
separately from validator output.

### GVI-H02 — Proof coherence weakness

**Hypothesis:** P1 does not establish a causal or integrity-preserving
relationship between gate execution and textual PASS evidence.

**Prediction:** a gate that exits nonzero plus evidence containing the expected
milestone and `PASS` will be accepted.

**Falsification:** P1 rejects the case using an executable gate/evidence linkage,
recorded exit status, gate identity, or equivalent coherence proof.

**Observation:** preserve gate bytes, direct execution result, evidence bytes,
and validator result as distinct fields.

### GVI-H03 — Historical ordering weakness

**Hypothesis:** P1 accepts some valid current tuples without establishing that
the transition into the tuple is legitimate.

**Prediction:** after committing A0, then A1, restoring the individually valid A0
tuple will still be accepted.

**Falsification:** P1 detects and rejects the rollback through an explicit
ordering or predecessor invariant.

**Observation:** preserve each committed project-state tuple and validate A0,
A1, and rolled-back A0 independently.

### GVI-H04 — Artifact-authority weakness

**Hypothesis:** P1 has no executable discovery and precedence rule for
contradictory verification claims across project state and experiment records.

**Prediction:** adding individually schema-valid contradictory experiment
records will not change validation of an otherwise accepted established state.
The P1 EMPTY sentinel case may already fail for an unrelated missing-path
reason and must not be misreported as contradiction detection.

**Falsification:** P1 discovers the governed experiment records and rejects the
specific contradiction with an authority/consistency diagnostic.

**Observation:** independently schema-check each experiment record, then invoke
P1 and inspect the validator source for discovery rules.

### GVI-H05 — State/transition separation

**Hypothesis:** isolated state validity and transition validity are distinct.

**Prediction:** A0 and A1 tuples will each validate in isolation while the
sequence A0 → A1 → A0 remains accepted because P1 checks only the current tuple.

**Falsification:** either one isolated tuple is invalid for its own reasons or
P1 implements a transition relation that rejects the rollback.

**Observation:** compare isolated validation results with the committed sequence.

### GVI-H06 — Executable semantic authority

**Hypothesis:** verification meaning is duplicated across schema, validator,
policy, documentation, tests, and artifact records sufficiently to permit
semantic divergence.

**Prediction:** at least one policy or artifact-level invariant will lack a
shared executable representation, and at least one accepted fixture will
contradict that narrative invariant.

**Falsification:** one reusable executable semantic authority is shown to govern
classification, proof, transitions, and artifact consistency without divergent
reimplementations.

**Observation:** map each verification claim to its defining and enforcing
artifacts, then compare controlled results.

### GVI-H07 — Fail-closed strengthening feasibility

**Hypothesis:** provenance, coherence, and ordering can be strengthened without
rejecting legitimate existing governed states.

**Prediction:** candidate invariants can be stated consistently with Praxis P1,
SRF P1, and controlled valid histories.

**Falsification:** every plausible strengthening invalidates a legitimate
observed state or requires assumptions unsupported by evidence.

**Observation:** compare proposed invariants with read-only existing practices.
Without an implementation candidate and adversarial regression, the result must
remain bounded and may be `INCONCLUSIVE`.

## Planned scenario families

```text
PROVENANCE
tracked in claimed commit
tracked only after claimed commit
untracked gate
untracked evidence
external gate
external evidence
changed bytes after claimed commit

COHERENCE
successful gate + PASS text
failing gate + PASS text
successful gate + non-PASS text
evidence checksum match/mismatch/absent

ORDERING
A0
A0 -> A1
A0 -> A1 -> A0
unrelated repository commits
invalid intermediate state followed by repair

AUTHORITY
project-state A0 + manifest A0
project-state A0 + manifest A1
project-state evidence A + manifest evidence B
project-state gate A + manifest gate B
orphan VERIFIED manifest
```

## Evidence sources

- exact P1 schema, helper, and validator identities;
- generated Git repositories with recorded object and tracking facts;
- direct gate execution outputs;
- JSON Schema results for experiment records;
- committed state snapshots and validator outputs;
- read-only Praxis, rejected PBG, and SRF identities.

## Stop rule

Stop after reproduction, classification, candidate invariants, and a bounded
semantic architecture proposal. Do not change production validator, schemas,
policy, or templates; do not merge, promote, declare P2, or modify SRF.
