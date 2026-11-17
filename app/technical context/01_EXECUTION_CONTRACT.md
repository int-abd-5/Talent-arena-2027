---
doc_id: EXECUTION-CONTRACT
document: Implementation Readiness and Execution Contract
purpose: Make the specification executable as bounded implementation work without confusing specified controls with verified capabilities.
audience: lead engineering agent; implementation agent; technical reviewer
stability: review
as_of: '2026-11-17'
---

# Implementation Readiness and Execution Contract

The execution entry point for an implementation agent. It does not replace the domain contracts with a
summary. Product truth, numbered specifications, ADRs and memory are the only canonical documentation
hierarchy. Current implementation state is owned by the top of
[BUILD_PROGRESS](BUILD_PROGRESS.md). Local experiments are not delivered capabilities.

## Engineering baseline

```yaml
# artifact: IMPLEMENTATION_BASELINE
architecture:
  retain: modular application monolith; one system of record; isolated untrusted workloads
  rationale: >
    Fill in: what the principal complexity of MTAH 2027 Possession actually is. Reducing integration
    breadth is sensible; removing uncertainty handling, isolation or egress controls is not.
    Reopen decisions against their written reasons and evidence.
  technology_record: ADR-0001
product_boundary: >
  Fill in the working hypothesis about the first customer and use case. Customer access, observed
  workflow, source rights and willingness to pay must be evidenced; no package choice establishes them.
proof_boundary:
  rule: >
    A test proves the behavior it asserts, not the behavior it was never asked about. Independent
    expected results, negative paths and an adversarial review are required before a capability that
    can cause external harm is enabled.
```

## Build vertically

```yaml
# artifact: SLICE_SEQUENCE
B0:
  scope: reproducible workspace and verification pipeline; synthetic data only
  deliver: lockfile; pinned runtime; type, lint, unit, integration and browser commands; CI mirroring the local check
  exit: a fresh checkout runs the documented checks; a deliberate bad source fails each gate
B1:
  scope: executable core semantics and, where the core carries rules, an independent oracle
  deliver: typed models; reviewed expected results authored from the contract; separate adversarial fixtures
  exit: every state of the core's vocabulary is reachable and tested; unknown and conflict are preserved, never defaulted to success
B2:
  scope: security and tenancy irreversibles, before any real data
  deliver: authenticated scope; isolation enforced by the engine; sensitivity classification; key separation; tamper-evident audit; retention hooks; safe logs
  exit: cross-tenant negative tests; denied reads and writes; tamper detection; restore evidence
B3:
  scope: one end-to-end synthetic path with a real UI
  deliver: the thinnest real slice from input to a human-reviewable result
  exit: the path is inspectable, an unknown outcome has a response path, and a browser test drives it
B4:
  scope: fake external effects through reconciliation
  deliver: transactional outbox; fenced work claims; a fake destination with a controlled clock and call ledger
  exit: accepted-then-timeout, duplicate response, stale worker, changed input and partial success each handled; no blind resend
B5:
  scope: one design-partner cohort
  deliver: agreed scope; minimal real integration; measured baseline; human-reviewed operations
  exit: integration and pre-real-data gates; rights; named owners; an enabled-capability release suite
ordering:
  rule: >
    B0 and prototype UI research can proceed while customer validation runs. B1 precedes any consumer
    of the core. B2 precedes real data. B4 precedes live external effects. B5 does not authorize autonomy.
  why: >
    The plan is a scope map, not a requirement to finish every backend before inspecting a user's
    workflow. Prototype projections early; activate production actions only after their dependencies.
```

## Contract for every implementation task

```yaml
# artifact: AGENT_WORK_CONTRACT
required_input:
  - owning module and the source artifacts, with the rationale sections read
  - bounded behavior change and explicit non-goals
  - allowed files and named interface dependencies
  - failure example, acceptance assertions and verification commands
  - data classification and possible external effects
execution:
  - write and run the failing test before implementing behavior
  - implement one boundary at a time; deterministic domain modules have no I/O
  - validate untrusted inputs and deny missing authorization context
  - regenerate rather than hand-edit generated output
  - run affected regression tests and the slice's full verification gates
  - obtain independent review of domain, security and integration changes
required_output:
  - changed files and symbols
  - tests actually executed, their outcomes, and the paths left untested
  - generator and oracle provenance where they apply
  - residual risks and decision implications
  - updated implementation status in BUILD_PROGRESS and memory
quality_floor:
  coverage: at least 80 percent with explicit includes; no excluding new logic to meet the threshold
  nonnegotiable: no silenced checks, deleted assertions, skipped failures or permissive stubs to obtain green
  important_limit: coverage alone does not prove semantics; independent expected results and negative paths are required
  exceptions: reason, owner, affected paths and expiry recorded and reviewed
context_use:
  rule: >
    Graphify and the project brain locate source documents. Read the authoritative artifact before
    modifying it. Treat inferred graph edges and historical memory as evidence to verify, not as
    requirements.
  parallelism: independent modules only; explicit file ownership; one integration owner; do not spawn copies of the whole project
```

## Integrate against evidence

```yaml
# artifact: INTEGRATION_READINESS
rule: a supported standard does not establish that a particular customer's deployment exposes it
first: minimum usable read integration agreed with the partner; do not gate initial value on write-back
simulator:
  contract: controlled clock; recorded call ledger; independently authored faults; versioned fixtures
  essential_faults: [failure_before_send, accepted_then_timeout, duplicate_ack, conflicting_terms, stale_worker, changed_input, explicit_block]
  limitation: proves our handling, not the real counterparty's conformance or exactly-once external effects
```

## Evidence before activation

```yaml
# artifact: RELEASE_EVIDENCE
merge:
  requires: affected regression suite; source and generator drift; types; lint; dependency checks
  rule: unimplemented capabilities are explicitly disabled, not represented by skipped passing tests
live_data:
  requires: all security and privacy controls, authenticated scope, source access rights, approved subprocessors, threat review, restore evidence and named security ownership
live_effects:
  requires: validation of what is sent, current-version checks, suppression and kill-switch tests, destination verification and uncertain-outcome recovery
autonomy:
  requires: eligibility evidence and per-scope promotion gates
  rule: never infer zero true error probability from a finite sample with zero observed failures
targets:
  rule: >
    Performance targets, retention periods and timer defaults remain drafts until their authority and
    approval are recorded. Local benchmarks cannot validate customer commitments.
```

## Remaining decisions

List here, as a table or a YAML artifact, each decision the owner still owes, what is blocked on it and
who decides. An unresolved item is written down; it is never answered by invention.
