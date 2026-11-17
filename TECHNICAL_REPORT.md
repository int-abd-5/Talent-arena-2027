# STAR STRUCK - Phase 1 report

More Than A Hack 2027 | 17 November 2026

## What the labels mean

The CSV has one row for every video frame. `H` means Barcelona has the ball while play is live. `A` means Athletic Club has it. `D` means the ball is not in play. `X` means the program has no label, or the frame has no ground truth.

The ranking is based on possession spells, not only frame-by-frame accuracy. A false short spell or a missed change of team can lower the score. On scored frames, `X` counts as a miss for `macroF1`. For `spellF1`, the scorer carries the previous label across an `X`, which can be costly when possession changes. [Scoring details](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/EVALUATION.md)

## How the program works

It processes each half separately and uses player positions, ball movement, and automatic Smart Tags to choose a label for each frame.

| Evidence | How it is used |
|---|---|
| Player and ball movement | Coordinates are converted to metres. A nearby player is stronger evidence when the player and ball move together. A sudden change in the ball's speed or direction can also indicate contact. |
| Fast or missing ball tracks | A fast ball makes simple player proximity less reliable. A short gap of up to 0.28 seconds can be interpolated with lower confidence. Longer gaps need other evidence before they support a stoppage. |
| Stoppages and restarts | The program checks whether the ball is outside the pitch, still near a line, or moving slowly while players also slow down. A set-piece tag helps identify a restart when play resumes. |
| Phase tags | Tags are softened at their edges. Tracking evidence still takes priority when it clearly shows control. |

The program uses a sequence decoder so one uncertain frame does not immediately change possession. Strong evidence of control makes a handover more likely. Evidence of a ball exit or restart makes a change to or from `D` more likely. At the start of a half, sustained ball movement near midfield helps locate the kickoff. If that cue is missing, the kickoff tag provides the timing. [Organizer FAQ](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/FAQ.md)

The 2026 winning project also used player and ball movement to infer passes and interceptions. We used that idea to guide our tracking features. [Project notes](https://adriaflores.com/projects/soccer-gpt/)

## Data and checks

The program reads the tactical ATD tracking files and Smart Tagging XML. The tracking gives XY positions and team assignments for track slots, but no lasting player IDs. Ball movement is calculated from its XY path. The model does not use either video, the homographies, or the broadcast tracking. The tactical ball is missing in about 41% of the scored frames, so the model also uses player movement and tags to handle gaps. [Organizer data guide](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/DATA.md)

We did not fit model weights. We compared settings on two other DFL matches and held a third match out for the final check. The public DFL possession labels were used only to score those matches. Synthetic cases check the program's behavior. The five-minute competition reference was used only to check the frozen pipeline, not to tune it. The DFL dataset is released under CC BY 4.0. [DFL dataset](https://doi.org/10.6084/m9.figshare.28196177.v1) | [Dataset paper](https://doi.org/10.1038/s41597-025-04505-y)

On the two development matches, average `spellF1` was 0.5031 with the original tracking. The nearest-player baseline scored 0.3310. When 40.7% of ball positions were hidden in seeded gaps, our model scored 0.4219 and the baseline scored 0.2250. The selected turnover penalty is 2.5, the stoppage penalty is 4.0, and the stoppage evidence bias is 0.05.

The model also scored higher than the baseline on the held-out DFL match, which had 141,561 scored frames.

| Holdout condition | Baseline spellF1 | Model spellF1 | Baseline macroF1 | Model macroF1 |
|---|---:|---:|---:|---:|
| Original tracking | 0.2838 | 0.4518 | 0.3488 | 0.8253 |
| 40.7% of ball positions hidden | 0.2015 | 0.3213 | 0.3700 | 0.7823 |

The official validator accepted the CSV. A clean checkout at `ce15511` reproduced it byte for byte. On an M1 Pro Mac, one run took 3.52 seconds and used about 441 MiB of memory. The repository contains the benchmark code and the development results.

## Limits

XY positions alone cannot identify every aerial duel, deflection, or referee whistle. A long gap that overlaps a turnover can extend the previous possession. Automatic tags can be early, late, or wrong. The outside matches do not have the same Metrica tags, and the DFL tracking sometimes leaves the ball still during a stoppage. These results do not predict the private-match score or ranking.

## Recreate the CSV

Use Python 3.12.14 and the locked environment. The data folder must contain these three files:

```text
tactical/BAR-ATH_tactical_atd.txt
tactical/BAR-ATH_tactical_atd.xml
tactical/BAR-ATH_tactical_smart_tagging.xml
```

Run:

```sh
uv sync --locked
uv run --locked python -m app.possession --data-dir data --output 'outputs/STAR STRUCK.csv'
uv run --locked python ../more-than-a-hack-2027/evaluation/validate_submission.py \
  'outputs/STAR STRUCK.csv'
```

The verified CSV has SHA-256 `221d63f41bc40675dcd389c9e838fda3d1af9bbdb1727ea787c058a09fe13881`. [Official validator](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/evaluation/validate_submission.py)
