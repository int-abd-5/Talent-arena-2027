# STAR STRUCK | Phase 1 technical report

**More Than A Hack 2027 · 17 November 2026**

## Method

The estimator finds a single sequence of team possession and stoppages on the tactical timeline.
Each half is decoded separately as three states, Barcelona (`H`), Athletic Club (`A`) and dead
ball (`D`). The remaining frames use `X` according to the organizer's published bounds. The
ranking metric matches same-team possession intervals by temporal overlap, so an extra short
spell or a missed stoppage can cost a match even when most individual frames are correct.
[Scoring specification](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/EVALUATION.md)

| Evidence | How it influences the sequence |
|---|---|
| Team control | Convert coordinates into metres. A close player provides stronger evidence when ball and player move together or when a nearby change in ball motion suggests contact. Use the strongest signal per team. |
| Loose balls and gaps | Fast ball travel reduces the weight of proximity. A plausible gap of up to 0.28 seconds can be interpolated at reduced confidence. Longer gaps lower certainty and contribute to stoppage evidence only with additional signals such as player slowdown or an observed ball exit. |
| Stoppages and restarts | Ball position beyond the pitch, stationarity near a line and slow collective movement favor a stoppage. A set-piece tag supports a restart when ball motion resumes. |
| Automatic phases | Taper each tag at its edges. Bound overlapping support and give stronger weight to tracking when it shows clear control. A restart tagged `N/A` provides timing context. |

Viterbi decoding adds a cost to each state change. Strong control reduces the cost of a team
handover, while evidence of an exit or a restart reduces the cost of entering or leaving dead
ball. An isolated touch that produces only weak or short-lived evidence will usually leave the
current spell intact. After a stoppage, the new team is inferred from control and restart cues.
Offline decoding uses evidence on both sides of a candidate boundary without carrying a state
across halves. The use of ball motion and player configurations is consistent with work on
tracking-based event detection. [Vidal-Codina et al.](https://arxiv.org/abs/2202.00804)

## Inputs and validation

The prediction command reads the tactical ATD text and metadata XML plus the tactical Smart
Tagging XML. The ATD frame ID is one above the CSV frame index. Tracking provides normalized
XY positions and team assignments for slots, so the model needs neither player identities nor
video pixels. Ball motion comes from the XY trajectory. Both videos, both homographies and the
broadcast tracking were outside the inference pipeline. The supplied tactical ball is missing
on about 41% of graded frames, and the broadcast has its own timeline.
[Organizer data reference](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/DATA.md)

**Label provenance.** No model weights were fitted. We used public frame-level DFL ball status
and possessing team from Bassek et al.'s CC BY 4.0 IDSSE release to compare decoder penalties on
two other matches and reserved a third match for the locked system. The provider's documentation
describes the fields and its quality controls. It does not name individual frame annotators.
Synthetic cases check the software's behavior. The five-minute competition reference is reserved
for a pipeline check after model selection.
[DFL dataset](https://doi.org/10.6084/m9.figshare.28196177.v1) ·
[Data publication](https://doi.org/10.1038/s41597-025-04505-y)

On the two development matches, average possession spell F1 with original observations was
**0.5085** versus **0.3310** for the nearest-player baseline with a centered ±2 second vote. With
40.7% of ball positions hidden in seeded contiguous gaps, it was **0.4275** versus **0.2250**.
The selected turnover penalty is 2.5, the stoppage penalty is 4.0 and the stoppage score bias is
0.05. [Development comparisons](app/technical%20context/adr/0002-temporal-possession.md)

## Limitations

Player and ball XY can’t reliably distinguish every aerial duel, deflection or referee whistle.
A long gap that straddles a turnover can extend the preceding spell. Set-piece and phase tags
can be early, late or incorrect. No external match had these Metrica tags, so the benchmark
measures the tracking and decoding parts of the method. DFL tracking also sometimes freezes the
ball during stoppages. Independent masking preserves that artifact and does not reproduce every
real cause of ball loss. These scores do not predict rank on the private match. The next useful
experiment would be adding a local cue for confirmed restarts and evaluating it on independent
matches with comparable ball loss.
[External benchmark recipe](app/tools/DFL_BENCHMARK.md)

## Reproduce the CSV

Use Python 3.12.14 and the locked environment. Point the command at the supplied data bundle with
its three canonical tactical inputs. It writes the full tactical frame sequence, including all
199,319 rows.

```sh
uv sync --locked
uv run --locked python -m app.possession --data-dir data --output 'outputs/STAR STRUCK.csv'
```

Run the [official validator](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/evaluation/validate_submission.py)
with the same environment on the generated CSV. The [project README](README.md) gives the
relative path for using a sibling organizer clone.
