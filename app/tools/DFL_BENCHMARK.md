# Possession benchmark on public DFL matches

The benchmark uses other matches with frame labels to compare the estimator with the organizer's
nearest-player baseline. The Phase 1 match and its reference labels are outside the benchmark.

| Split | DFL match IDs | League |
| --- | --- | --- |
| Development | `J03WOH`, `J03WQQ` | 2. Bundesliga, 2022–23 |
| Holdout | `J03WN1` | Bundesliga, 2022–23 |

The split is by match. Use development to compare variants and run holdout after fixing a candidate.
The benchmark imports the organizer's scoring functions and the centered ±50-frame vote from the
official clone. Each half is inferred on its own. The scorer excludes `X` frames and matches
possession spells separately across the gap between halves.

## Source and label meaning

Deutsche Fußball Liga (DFL) provided the IDSSE dataset under CC BY 4.0. Bassek, Rein, Weber and
Memmert published it in 2025. The archive contains 25 Hz TRACAB tracking from multiple cameras.
The paper describes visual quality controls and identifies what the ball state and possession fields
mean. It does not assign the frame labels to named individual annotators. The loader uses the
publisher's original metadata and position XML for each match from Figshare version 1 and verifies
the published MD5 digests. The predictor receives player and ball XY, team membership, frame rate and
pitch dimensions. Ball height, events, and reference labels are excluded from its inputs.
[Dataset](https://doi.org/10.6084/m9.figshare.28196177.v1),
[publication](https://doi.org/10.1038/s41597-025-04505-y).

The adapter joins players to ball records by the original frame number within each half. It converts
the source's pitch centered positions in metres to coordinates normalized by the reported pitch
dimensions. `BallStatus=0` maps to `D`, and `BallStatus=1` maps documented `BallPossession` values
`1` and `2` to `H` and `A`. Unknown states and missing reference rows remain `X`.

## Reproduce

Run these commands from the submission repo with the organizer's clone next to it. To point scoring
to a different copy of the official clone, pass its path with `--official-repo`.

```bash
uv run --locked python -m app.tools.dfl_benchmark prepare --split development
uv run --locked python -m app.tools.dfl_benchmark score --split development
uv run --locked python -m app.tools.dfl_benchmark prepare --split holdout
uv run --locked python -m app.tools.dfl_benchmark score --split holdout
```

The adapter reports JSON with match, split, condition, method, actual missing fraction, official
`spellF1` and `macroF1`, dead-ball F1 and spell counts. Use `--condition original` or
`--condition masked` to run a single condition and `--baseline-only` for the nearest-player baseline.
`--solver-kwargs` passes a JSON object of keyword arguments to the estimator. The default cache is
`data/external_dfl/`, which holds about 1.2 GB of source XML and derived arrays for the three matches.

Each match is measured with the original ball observations and with 40.7% of frames blanked in
contiguous blocks. The stress condition partitions each half into blocks of 5–100 frames and hides
blocks in deterministic random order until it reaches the target fraction. It uses NumPy's default
generator with seed components `20271117`, the base 36 match ID and half number. Already missing
observations remain missing. The published percentage is the resulting missing fraction among
graded frames. The masking reads array lengths only.

This is an external comparison of tracking, motion and temporal inference. The German matches use
different cameras and tracking quality, and the benchmark does not have Metrica Smart Tags. The
ball is often recorded as stationary in these files. On the two development matches, the 90th
percentile of dead-ball XY speed measured over a 0.24 second window was zero. This property can
make stoppage detection easier than it is with tactical tracking. The artificial gaps do not
capture every cause of lost ball tracks. The holdout score measures performance on one German
match with these differences in observations. The Phase 1 rank requires the organizer's scorer
and hidden reference on the competition match.
