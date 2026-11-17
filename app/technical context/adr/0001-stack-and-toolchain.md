# ADR-0001: Stack and toolchain

- **Status**: proposed
- **Date**: 2026-11-17
- **Deciders**: Mohib
- **Supersedes**: none

## Context

MTAH 2027 Possession needs a reproducible workspace and a verification pipeline before any product code,
because every later quality claim rests on checks that run unattended. The scaffold chose a default so
B0 could start; this record states it, so it can be challenged rather than inherited.

## Decision

Not yet chosen. B0's first task is to choose the language, runtime, type and lint tooling, test runner,
coverage tool and CI, and to replace this section with the decision. Until then no product code is written.
- **Persistence, hosting, model providers and other vendors:** not chosen. Each is its own ADR when it is
  needed, with a revisit trigger.

## Alternatives considered

Fill in as the decision is challenged. At minimum record the runtime and test-tool alternatives that were
proposed and why they lost, so they are not reintroduced by accident.

## Consequences

Strict types and a single formatter make early work slower and later refactors cheaper. Running a fresh
checkout's full check becomes a milestone gate. The cost is a pinned toolchain that must be bumped on purpose.

## Revisit trigger

Reopen when the full local check exceeds ninety seconds on the owner's machine, when a required library
no longer supports the pinned runtime, or when the owner decides the product needs a stack this one cannot host.
