# Qualifier validation | 17 November 2026

Production code checked at `ce15511`. The official validator, scorer and baseline came from
the separately cloned Metrica repository at `f8f2629`.

## What was checked

| Check | Result |
|---|---|
| Synthetic behavior and software checks | 18 passed, with 94.25% statement coverage for the prediction package. Ruff, mypy, workspace checks and the locked runtime dependency audit passed locally. |
| Independent possession expectations | Synthetic scenarios cover loose balls, short gaps, sustained handover, stoppage and restart, stationary home control, team symmetry and absent tracking. |
| Two regressions | The long no-signal gap and the graded prefix before kickoff both failed before the corresponding fixes and passed afterward. |
| Official baseline | Regenerated `baseline_smooth50.csv` with the official starter and matched the committed output byte for byte. |
| Exact output | The official validator accepted `STAR STRUCK.csv` with 199,319 rows, frames 0 through 199,318. |
| Public scoreboard smoke check | The locked candidate ran through the official scorer on its public five-minute window. Its result was outside model selection. |
| Reproduction | A detached clean checkout installed the same lock, ran `make check` and regenerated the official-format CSV byte for byte. |
| Hardware | One run on this M1 Pro Mac took 3.52 seconds and reported 462,569,472 bytes of peak resident memory. Environment setup is excluded. |

## Why the approach was chosen

The external comparison used only DFL matches. Two 2. Bundesliga matches provided 279,559
graded development frames. J03WN1, the reserved Bundesliga match, provided 141,561 graded
frames. The DFL ball status and team fields were labels for scoring. Only player and ball XY
and geometry went into external inference. The alternate prediction method is the organizer's
nearest-player rule with its centered ±50-frame vote. [Benchmark recipe](../../tools/DFL_BENCHMARK.md)

| Condition | Mean development spellF1 baseline / model | Holdout spellF1 baseline / model | Holdout dead ball F1 baseline / model |
|---|---:|---:|---:|
| Original tracking | 0.3310 / 0.5031 | 0.2838 / 0.4518 | 0.0000 / 0.9306 |
| Ball XY hidden for 40.7% of frames | 0.2250 / 0.4219 | 0.2015 / 0.3213 | 0.1395 / 0.9189 |

The early implementation scored the reserved match in a local run. Those metrics were left
unread when independent QA exposed the unsupported stoppage bias. The two synthetic regression
cases drove the fix, and the configuration was rechecked only on development matches before
the reported holdout run. [Decision record](../adr/0002-temporal-possession.md)

The gap test removes ball observations in contiguous blocks and leaves the players intact.
DFL tracking quality, ball status patterns and team labels can differ from the competition's
correction workflow. The external experiment says little about the effect of automatic Metrica
tags and does not determine the private score or top-20 placement.

## Reproduction receipt

```text
221d63f41bc40675dcd389c9e838fda3d1af9bbdb1727ea787c058a09fe13881  STAR STRUCK.csv
```

The output and source data stay on the local machine. The local repository is ready for review
before the owner authorizes publication. The exact time for the submission cutoff must come
from the organizer's participant instructions. [Submission process](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/SUBMISSION.md)
