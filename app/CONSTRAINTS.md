# Constraints

Current implementation status and last milestone evidence live at the top of
[BUILD_PROGRESS](technical%20context/BUILD_PROGRESS.md). This file owns quality requirements; dated
measurements below are historical evidence, not a second live status.

This file is the project's quality bar as a contract. It is the `quality_floor` of the
[execution contract](technical%20context/01_EXECUTION_CONTRACT.md) made mechanical. Where a row cites an
artifact, **the artifact is authoritative and this file is the enforcement**; if they disagree, the
artifact wins and this file is wrong.

## Floor (always enforced, no setup required)

- No new suppression comments: `@ts-ignore`, `@ts-expect-error`, `biome-ignore`, `eslint-disable`, `noqa`
- No unimplemented stubs: `throw new Error("Not implemented")`, empty `catch {}`, placeholder returns
- No skipped or deleted tests without a reason in the commit message
- No secrets in source, and no credential or token in any file that is pushed
- Every commit is authored and committed by Mozenjii, with no AI attribution (`.githooks/`)
- No generated file is ever hand-edited
- This file does not get weakened to make a change pass

The last line is load-bearing. A lowered threshold in the same commit as the change that failed it is
the mechanical form of simplifying away a decision someone made for a reason.

## Enforced with numbers

No toolchain exists yet. B0 chooses one, records the choice as an ADR, and fills this table with one
row per dimension — documentation, types, lint and format, unit and integration, coverage (≥ 80% over
explicit includes), dependency risk, browser or end-to-end flows — each naming its command, when it
runs, and why the rule exists. A row that cannot run yet belongs in "Not yet applicable", not here.

Every gate must run unattended in CI as well as locally. A gate that only runs when someone remembers is
not enforced. Watch each gate fail once on a deliberate bad input, so you know it is connected.

## Measured, not yet enforced

Ratchets: each row says what is measured, today's figure and the direction it must move, and names the
wrong way to move it (usually deleting the check).

| Metric | Today | Direction |
|---|---|---|
| — | — | — |

## Not yet applicable

Recorded so their absence is a decision rather than an oversight. Each is a real gate for its slice.

| Dimension | Gate | Slice |
|---|---|---|
| Accessibility | Zero critical or serious axe violations | the slice that delivers a UI |
| Performance budgets | LCP and CLS against a running preview | the slice that delivers a UI |

Accessibility and performance need a URL. Inventing a check that cannot run is how a bar becomes
decoration.

## Exceptions

| ID | Rule | Path | Reason | Owner | Expires |
|---|---|---|---|---|---|
| — | none | — | — | — | — |

An exception needs a reason, an owner, the affected paths and an expiry.
