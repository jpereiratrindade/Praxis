# PRAXIS-LIC-001 — Governed project licensing

Status: experimentally closed (not a promoted method rule)

## Function and evaluation boundary

A maintainer constituting a new governed project needs an explicit, auditable
licensing decision. The Praxis default may fill an unmade choice only inside a
positive initial-constitution boundary; it must never turn missing metadata in
an existing project into permission to create or replace a license.

This experiment evaluates deterministic engineering-policy coherence,
provenance, artifact identity, bootstrap monotonicity, and compatibility with
Method 0.1 projects. It does not offer legal advice, establish universal
license compatibility, or validate external institutional policy.

## Baseline preserved before implementation

Observed at Git `c3e24973a2a9c14bd44c4efa6c932ccb88a0c84e` on 2026-08-17:

- the Praxis `LICENSE` SHA-256 was
  `3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`;
  its text identifies GNU GPL version 3 and the repository declares Praxis as
  `GPL-3.0-only` in its existing SPDX notices;
- the governed-project template SHA-256 was
  `d0e609272046673db902eee00f96f8481fe894b695f8dc5dd9a84898828f9e3b`
  and contained no licensing state or initial-constitution capability;
- `project-state.schema.json` SHA-256 was
  `f7771bd32acd3bd279ca6e813f1c722d5f19d9c97ffcd85dfe62701e6e0bf20d`;
- `validate_governed_project.py` SHA-256 was
  `df1e6f4a9f6263861c62c68527a0a219b9926535e6cf9d62999da8a7bc8109cc`;
- the methodology validator and Praxis governed-project self-validation both
  returned zero and reported ready;
- all four compiled CTest suites passed;
- the generic validator checked that Praxis had a declared gate/evidence and
  that referenced bootstrap scripts existed, but did not constitute or verify
  a licensing decision;
- absence of licensing metadata was accepted. This preserved legacy projects,
  but could prove none of explicit/default provenance, license-artifact
  coherence, exception rationale, or licensing-bootstrap monotonicity.

These observations are the pre-intervention baseline; later evidence is not
used to reconstruct it.

## Initial prediction

The smallest coherent extension is expected to be an optional, flat licensing
state beside the existing flat project state, a consumed creation capability
present only in the new-project template, one create-once constitution command,
and validation composed into the existing governed-project validator.

If this framing is sound, executable scenarios should show all of the
following:

1. missing licensing state remains valid for a legacy Method 0.1 project and
   never causes mutation;
2. default resolution is impossible without the positive creation capability;
3. explicit, default, and policy-exception provenance are distinguishable from
   the resolved identifier;
4. an exception without rationale and a changed/missing license artifact fail;
5. a repeated constitution preserves bytes and provenance;
6. Praxis continues to validate without new licensing metadata and its
   `LICENSE` hash remains the baseline hash.

The evaluation boundary is local filesystem behavior under the supplied
bootstrap and validator. It does not claim to detect coordinated edits to both
metadata and artifact, identify arbitrary legal text, or determine legal
compatibility.

## Minimum ontology and implementation choice

The proposed state composes a few flat values rather than adding a general
policy engine:

- `resolved` records the governed SPDX-like identifier;
- `provenance` is one of `explicit`, `default`, or `exception` and therefore
  distinguishes how the same resolved value was reached;
- `policy` and `policy_default` identify the internal rule evaluated;
- `exception_rationale` exists only for a real exception;
- `artifact` and `artifact_sha256` bind the decision to the materialized file;
- a template-only `.hoa/initial-constitution` capability proves the operation
  is running in the governed creation boundary and is consumed on success.

Within this representation, an explicit value different from the default is
still `explicit`, not `exception`. A policy exception is a separate invocation
and requires its rationale. The artifact hash proves deterministic byte
identity, not a legal interpretation of its contents.

Materially plausible alternatives considered before implementation:

- adding all licensing fields to `project-state.yaml` was rejected because it
  couples an optional Method 0.1 capability to milestone state and requires a
  fragile rewrite of that canonical file during constitution;
- treating missing licensing metadata as the bootstrap boundary was rejected
  because it makes absence an authorization and would silently endanger legacy
  projects;
- introducing a general policy manifest/engine was rejected because one fixed
  prospective default and three provenance states do not justify that layer;
- inferring a license identifier from arbitrary legal text was rejected as
  unreliable and beyond the bounded engineering claim;
- supporting no independent exception state was rejected because the mission
  requires an executable distinction between normal explicit choice and an
  actual departure from an otherwise applicable default.

## Results and reflexive turns

The initial ontology survived implementation. The resulting slice consists of
one optional schema/state, one consumed template capability, a create-once
bootstrap, a read-only validator composed into the existing governed-project
validator, and an executable gate. No general policy engine or Method 0.1
version migration was needed.

The governed gate passed all 20 licensing scenarios, the repository-wide
quality gate passed all four compiled suites plus licensing tests, and a real
template-derived project was inspected through pending, constituted, validated,
and repeated-bootstrap states. The second bootstrap preserved the exact
`LICENSE` and `.hoa/licensing.yaml` hashes. Praxis remained legacy with respect
to the optional capability, remained valid, and retained its original
`GPL-3.0-only` declaration and `LICENSE` hash.

### Reflexive turn R1 — provenance-preserving requests

- Prior expectation: a canonical default artifact and byte-preserving repeated
  bootstrap would make provenance monotonic.
- Challenging observation: the first implementation slice also accepted a
  caller-supplied artifact during a default request and treated a same-license
  reexecution under different requested provenance as a harmless repeat.
- Why it mattered: those paths preserved bytes but blurred whether policy or a
  caller produced the resolution, weakening the human-auditable function.
- Bounded change: default resolution now always creates the governed default
  artifact; reexecution rejects requested license, provenance, or exception
  rationale that contradicts the constituted decision.
- Learning candidate: idempotence of bytes is insufficient when provenance is
  part of the governed state; request identity must also be monotonic.
- Scope and promotion: observed in this local licensing bootstrap and covered
  by adversarial tests; `promotion: candidate`, not a Method rule.

No other decision-changing surprise occurred. A mismatch between one test's
expected error wording and the implementation was routine test maintenance and
did not change framing or behavior.

## Evaluation

Technical verification supports the mandatory properties within the declared
boundary: explicit/default/exception provenance, exception rationale,
referential integrity, deterministic contradiction detection, monotonic
bootstrap, legacy compatibility, and Praxis self-license preservation.

Functional evaluation supports the intended non-relicensing behavior for the
exercised local workflows: missing metadata alone caused no mutation, an
existing `LICENSE` blocked default resolution, and only the positive template
capability enabled initial constitution. Whether the generated declaration is
appropriate for a particular project's legal or institutional circumstances
remains external human judgment and is not self-certified here.

The prediction therefore survived with a narrower request-identity condition.
The representation did not grow beyond the predicted optional state and
capability. Backward compatibility is demonstrated for the Praxis legacy state
and isolated legacy fixtures, not universally established for every external
Method 0.1 repository.

The validator deliberately cannot classify arbitrary license prose. It checks
schema/policy relations, artifact presence and hash, and—after the independent
audit described below—a mandatory matching SPDX declaration. A coordinated edit
of metadata, identifier, and artifact hash can form a new internally coherent
state and is outside the mutation-detection claim; Git review and project
authority remain responsible for authorizing such a new decision.

Candidate methodological learning (not promoted): absence of newly introduced
metadata should remain non-authoritative, while defaults that mutate governed
state require a positive, consumable creation capability. Evidence is local to
PRAXIS-LIC-001 and requires recurrence or explicit method governance before any
promotion.

## Independent audit reproduction and experimental closure

The closure cycle began from the same uncommitted working state above at
`HEAD=c3e24973a2a9c14bd44c4efa6c932ccb88a0c84e`. No PRAXIS-LIC-001 bytes were
staged or committed. Praxis `LICENSE` still matched both the recorded baseline
and `HEAD` at
`3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`.

### OBS-LIC-01 — bytes without declared license identity

Reproduced before correction. An isolated workspace received the recognized
capability, then ran explicit constitution for `MIT` with the repository
`CMakeLists.txt` as `--artifact-source`. That file had no SPDX declaration.
Bootstrap returned zero, generated `resolved: MIT`, `provenance: explicit`, and
artifact SHA-256
`13a33f5157f8262207896ee90d4e05423d2b34777e037c7b9c0f06f47494a28c`.
The read-only validator also returned zero.

The observation demonstrated only exact byte identity, not a deterministic
relationship between the resolved identifier and a declared artifact identity.
The correction requires every governed `LICENSE` to contain
`SPDX-License-Identifier: <resolved>` and rejects both an absent and a
contradictory declaration. It still makes no claim about the legal adequacy of
the remaining prose.

### Reflexive turn R2 — declared identity is part of materialization

- Prior framing: artifact presence plus SHA-256, with an SPDX comparison only
  when a declaration happened to exist, was sufficient bounded materialization.
- Observation: arbitrary non-license bytes could be constituted and validated
  as `MIT` while satisfying every hash claim.
- Why it mattered: the system could prove which bytes it governed but not the
  license identity those bytes declared, weakening the stated functional goal.
- Bounded change: a matching machine-readable declaration is now mandatory in
  both bootstrap and validator; no legal-text analysis was added.
- Learning candidate: artifact byte identity and artifact-declared semantic
  identity are distinct contracts and both must be explicit when both are
  claimed.
- Scope and promotion: demonstrated locally by OBS-LIC-01 and LIC-T12;
  `promotion: candidate`.

### OBS-LIC-02 — capability semantics

Reproduced before documentation correction. A new arbitrary directory with no
`.hoa/project-state.yaml` was given only a manually copied recognized
`.hoa/initial-constitution`. The validator reported constitution pending,
default bootstrap returned zero, resolved `GPL-3.0-or-later`, consumed the
marker, and the final validator returned zero.

The supported claim is therefore authorization, not historical origin: presence
of the recognized local capability authorizes initial constitution under the
Praxis policy. It does not prove that the directory was originally created from
the Praxis template. No cryptography, external authority, or new ledger was
introduced because historical-origin proof is not required by this milestone's
non-relicensing function.

### Reflexive turn R3 — authorization is not origin provenance

- Prior framing: the template-only marker was described as proving operation in
  the governed creation boundary.
- Observation: any local actor able to create the exact marker could establish
  the same accepted boundary in an arbitrary directory.
- Why it mattered: “template origin” would be a stronger historical claim than
  the implementation can demonstrate.
- Bounded change: policy, scenario, evidence, and experimental claims now name
  the marker as explicit local authorization; the implementation remains the
  same because that boundary satisfies the requested function.
- Learning candidate: a local capability can govern authority without proving
  historical provenance of its own creation.
- Scope and promotion: demonstrated for this filesystem capability only;
  `promotion: candidate`.

### Atomicity classification

Source inspection showed separately atomic writes followed by validation and
capability deletion. A fault injected specifically at `Path.unlink()` returned
nonzero after `LICENSE` and metadata existed. The capability remained and the
read-only validator rejected the state with “initial-constitution capability
was not consumed.” Thus full-sequence atomicity is not present, but the observed
failure is closed and explicit rather than silently accepted.

Classification: `bounded limitation` and `candidate future hardening`. A crash
earlier in the sequence can likewise leave an artifact without metadata; the
next default operation refuses to replace it. Recovery can require an explicit
operator decision. Transactional infrastructure is not justified within
PRAXIS-LIC-001 by the current evidence.

## Candidate Git/provenance learning

The closure kept the uncommitted working state, validated working state, commit
identity, verification, promotion, and publication distinct. This supports a
candidate methodological learning: Git commits and references are provenance
anchors, while verification, promotion, and publication are separate governed
transitions. This remains `promotion: candidate`; no Git subsystem or new
method milestone is introduced here.
