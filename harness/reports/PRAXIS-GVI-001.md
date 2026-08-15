# PRAXIS-GVI-001 — Governed verification integrity investigation

## First-cycle verdict

```text
READY_FOR_SEMANTIC_DESIGN
```

Praxis P1's verification-integrity problem is sufficiently reproduced and
bounded to design a candidate semantic model. This is not authorization to
implement, adopt, merge, promote, or declare Praxis P2.

P1 currently validates a useful but narrow set of facts: structural state,
current path existence, a permissive textual PASS pattern, an optional current
evidence checksum, and verified-commit ancestry. It does not establish proof
provenance, execution/evidence coherence, transition legitimacy, or authority
across verification-bearing artifacts.

## Starting Git state

```text
Praxis main:          e0532b8f5b9861c3047c0f1ab6173048cb445068
origin/main:          e0532b8f5b9861c3047c0f1ab6173048cb445068
gitlab/main:          e0532b8f5b9861c3047c0f1ab6173048cb445068
rejected PBG branch:  8f9b685c63617abb7eb02f574d0a74642c1f665d
GVI branch base:      e0532b8f5b9861c3047c0f1ab6173048cb445068
GVI branch:           investigate/governed-verification-integrity
working tree:         clean before investigation
```

The rejected PBG branch was published unchanged to GitHub and GitLab at
`8f9b685`. No merge or tag was created. GVI was then branched from authoritative
`main`, not from the rejected lineage.

## Baseline weakness reproduction

| Scenario | P1 result | Reproduced | Severity | Evidence |
|---|---|---|---|---|
| PARTIAL → EMPTY | REJECT | no | observation | `partial_to_empty` |
| PARTIAL → ESTABLISHED/restored | ACCEPT | yes | major | `invalid_state_recovery` |
| EMPTY + VERIFIED manifest | REJECT at `gate missing — NONE` | no; contradiction unobserved | major gap | `artifact_authority/empty_with_verified_manifest` |
| untracked gate | ACCEPT | yes | critical | `proof_provenance/untracked_gate` |
| untracked evidence | ACCEPT | yes | critical | `proof_provenance/untracked_evidence` |
| external gate | ACCEPT | yes | critical | `proof_provenance/external_gate` |
| external evidence | ACCEPT | yes | critical | `proof_provenance/external_evidence` |
| failing gate + PASS text | ACCEPT | yes | critical | `proof_coherence/failure_pass_no_checksum` |
| A0 → A1 → A0 rollback | ACCEPT | yes | major | `history_ordering` |

`PARTIAL → EMPTY` was a rejected-PBG candidate behavior, not a P1 behavior. P1
rejects the EMPTY sentinel because it interprets `NONE` as a path. Likewise, its
rejection of EMPTY plus a verified manifest is not contradiction detection: the
validator never mentions or reads the manifest.

The detailed machine-readable results and raw validator output are in
`harness/evidence/praxis-gvi-001/p1-observations.json`.

## Proof provenance findings

For gate and evidence, P1 establishes only:

```text
root / declared_path is currently a file
```

For the commit, P1 separately establishes:

```text
declared verified commit is an ancestor of current HEAD
```

It establishes no relationship between those facts. Every generated provenance
variant was accepted:

- gate and evidence tracked at the claimed commit;
- both tracked only after the claimed commit;
- untracked gate;
- untracked evidence;
- gate outside the repository;
- evidence outside the repository;
- gate bytes changed after the claim;
- evidence bytes changed after the claim.

Consequently P1 does not prove repository containment, Git tracking, historical
presence, or byte identity for proof artifacts.

The actual Praxis history adds an important boundary. Its gate exists at the
verified source commit `4389885`, with current and historical SHA-256
`246f76c11d601838a0ceb24668c243d404a1ae1d664e56d50bea52112dd61472`.
The governed evidence and checksum do not exist at `4389885`; they first appear
in closure commit `c3e2497`. A future invariant therefore cannot require
post-execution evidence to exist in the source commit. It must distinguish at
least:

```text
verified source commit
verification/gate identity
later verification-record commit
```

## Proof coherence findings

P1 does not execute the declared gate. Direct execution and validation were
recorded independently:

| Gate/evidence | Direct gate | P1 |
|---|---:|---|
| success + `A0 PASS` | 0 | ACCEPT |
| failure + `A0 PASS` | 9 | ACCEPT |
| failure + `A0 NOT PASS` | 9 | ACCEPT |
| failure + `A0 BYPASS` | 9 | ACCEPT |
| success + no `PASS` substring | 0 | REJECT |
| success + PASS + valid checksum | 0 | ACCEPT |
| success + PASS + invalid checksum | 0 | REJECT |

The regex accepts milestone and the substring `PASS` in either order. It does
not distinguish assertion, negation, or a larger word. A checksum, when present,
protects only current evidence bytes; it does not bind the evidence to gate
bytes, invocation, exit status, source commit, or historical execution.

The evidence favors two different operations:

1. **historical attestation validation** — establish what exact gate ran against
   what source, its recorded exit status/result, and the integrity of that
   record;
2. **current reproducibility assessment** — optionally rerun a current or
   historical gate and make a new observation under the present environment.

Re-execution must not silently replace the historical claim. Praxis P1's own
evidence records an earlier environment, while SRF demonstrates a richer
historical model containing protocol digest/archive, structured actions with
exit statuses, raw-evidence digests, pre/post state identities, and a chained
run record.

## State validation findings

Candidate minimum invariants for an isolated current state are:

1. JSON Schema proves structural shape only.
2. Proof paths are repository-confined and cannot escape through traversal or
   symlinks.
3. The claim identifies a verified source commit and a distinct verification
   record or closure commit.
4. Exact gate bytes are identified at a declared source/gate commit.
5. Evidence and a structured attestation are tracked and byte-identifiable at
   the record commit.
6. The record commit descends from the source commit and is reachable from the
   current governed history.
7. Canonical state points to one authoritative verification record rather than
   reconstructing proof from four unrelated strings.

The current P1 template illustrates the schema boundary: it structurally accepts
`A0 / 0000000 / scripts/verify_a0.sh / evidence-path`, but that tuple is not
semantically established by schema conformance.

## Transition findings

The individually valid A0 and A1 states both pass. Restoring the old A0 tuple
after A1 also passes. Therefore:

```text
validate_state(A0) = PASS
validate_state(A1) = PASS

does not imply

validate_transition(A1, A0) = PASS
```

Candidate transition invariants are:

- each new authoritative verification record references its predecessor or an
  append-only chain head;
- order is explicit rather than inferred from milestone spelling;
- Git ancestry is necessary provenance but insufficient methodological order;
- rollback cannot erase a later record;
- recovery or supersession preserves displaced and invalid history;
- state and transition validation produce separate results.

## Artifact authority findings

Two contract families can express verification-related claims:

- `.hoa/project-state.yaml`, treated by the validator as the canonical current
  state;
- experiment records, whose schema permits status `verified`, gate, evidence,
  and arbitrary additional metadata.

Praxis P1 has no automatic experiment-record discovery in its governed-project
validator. Six individually schema-valid records—matching, newer milestone,
different evidence, different gate, orphan VERIFIED, and VERIFIED beside
EMPTY—were never mentioned by validation. Established-state contradictions
were accepted. EMPTY was rejected only because of `NONE` path handling.

The policy says gates should reject divergence between canonical state,
manifests, and current-state documentation, but no shared executable discovery
or precedence rule implements that statement.

Candidate authority rules are:

- discover proof through explicit references or a governed registry, not broad
  filesystem scanning;
- canonical state is the current cursor;
- the referenced verification record carries proof authority;
- experiment/milestone `verified` status must link to that record or be treated
  as descriptive;
- contradictions among referenced authoritative artifacts fail closed;
- orphan records gain no authority merely from filename, directory, or status.

## Recovery semantics

```text
INCONCLUSIVE
```

P1 rejects a committed partial state and accepts the restored A0 state after it.
It neither examines nor classifies the repair as recovery. This demonstrates
that honest recovery is possible, but not whether Praxis should use a recovery
record, supersession edge, waiver, or another mechanism. That choice requires
semantic design and later governance review.

## Hypothesis outcomes

### GVI-H01 — SUPPORTED

All untracked, external, historically absent, and byte-mutated proof variants
were accepted.

### GVI-H02 — SUPPORTED

Gate exit status is unobserved; PASS, NOT PASS, and BYPASS evidence can all be
accepted through the same substring rule.

### GVI-H03 — SUPPORTED

A0 → A1 → A0 is accepted because P1 checks current-state ancestry, not
verification-history order.

### GVI-H04 — SUPPORTED

Schema-valid contradictory experiment records are not discovered. Policy intent
and executable enforcement diverge.

### GVI-H05 — SUPPORTED

Individually valid endpoint states form an accepted but semantically regressive
sequence, experimentally separating state and transition validity.

### GVI-H06 — SUPPORTED

Schema, template, validator, policy, and experiment records encode different
parts of verification meaning without a shared executable authority. The
controlled contradictions demonstrate material divergence, not merely code
duplication.

### GVI-H07 — INCONCLUSIVE

Praxis and SRF practices make a stronger design plausible, particularly the
source-commit/record-commit distinction and structured historical evidence.
No implementation candidate or adversarial compatibility audit exists yet, so
feasibility without legitimate-state regression is unproved.

## Candidate executable ontology

Evidence justifies a composable design direction, not an implementation:

```text
parse_and_validate_structure
        ↓
resolve_authoritative_verification_record
        ├── validate_proof_provenance
        ├── validate_historical_attestation
        └── detect_authoritative_artifact_contradictions

previous record + next record
        ↓
validate_transition

historical record + current environment
        ↓
assess_current_reproducibility
```

These should be small typed semantic operations reused by validator, CLI, tests,
and gates. The objective is one executable ontology, not one monolithic
function. Production API and storage format remain deferred.

## Rigor-level learning

```text
SUPPORTED AS CANDIDATE LEARNING
```

The PBG experience supplies direct evidence that methodological/governance
changes benefit from prediction-first work, preserved evidence, authority
separation, and independent attack: the original green candidate was rejected.
It does not establish the exact R0–R4 names or thresholds, nor that low-risk
changes need comparable ceremony. A graded model is worth designing later, not
adopting now.

## Unexpected observations

1. `A0 NOT PASS` and `A0 BYPASS` satisfy P1's PASS regex.
2. P1's actual self-governance evidence is absent from its verified source
   commit and legitimately arrives in a closure commit.
3. The current template is structurally schema-valid while its verification
   tuple is not semantically established.
4. P1 permits recovery from a historical invalid state but provides no explicit
   recovery semantics.
5. The GVI harness initially emitted nondeterministic temporary paths and commit
   identities; it was corrected so repeated runs now produce byte-identical
   evidence.

## Git state at stop

The GVI branch contains only protocol, experimental harness, generated evidence,
candidate learning, and this report. No production validator, schema, policy, or
template was changed.

```text
branch: investigate/governed-verification-integrity
main modified: no
GVI branch pushed: no
rejected PBG branch pushed: GitHub and GitLab only
merge performed: no
promotion performed: no
SRF changed: no
```
