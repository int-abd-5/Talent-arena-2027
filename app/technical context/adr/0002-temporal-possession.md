# ADR-0002 | Decode possessions with three states

**Status** Frozen for the development comparison on 17 November 2026.

## Decision

Score observations for home, away, and dead ball, then find the best path over each half with
Viterbi decoding. When the ball is well observed, favor control evidence from player distance and
relative motion. Carry or decay evidence through tracking gaps. Use sustained out-of-bounds
evidence, stationary ball near a line, and collective slowdown to distinguish stoppages. Add
automatic phase and restart tags as soft signals with tapered edges. Decode both halves separately.

A nearest player can change on a deflection. A missing ball can be in flight. A global moving vote
uses one window for live changes and real stoppages. The decoder adds an explicit cost to changing
state and reduces it when the observations support the new state. This targets the whole spell and
lets the offline path place a boundary near supporting evidence.

Multiply the stoppage bias by observed support for a stoppage. The initial additive bias could
turn a long gap with no signal into a spurious dead segment. Reduce the live offset with ball
visibility as well, so an unobserved interval can preserve either preceding state. An automatic
opening kickoff tag can identify a graded prefix before play. Find sustained movement near
the centre when tracking supports it, and otherwise use the beginning of the supplied window.
[Organizer FAQ](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/FAQ.md)

## Selection protocol

Use the organizer's spell F1 on two development matches from the public DFL IDSSE data, with
equal weight per match. Prefer spell F1 under 40.7% synthetic ball gaps and check the original
observations and secondary metrics. Reserve J03WN1 until the candidate is frozen. Tags are
available for the competition match and absent from this benchmark. Synthetic cases exercise
the tag adapter and semantics. [Benchmark recipe and provenance](../../tools/DFL_BENCHMARK.md)

| Turnover penalty | Stoppage penalty | Stoppage bias | Mean spellF1 with original tracks | Mean spellF1 with masked ball |
|---:|---:|---:|---:|---:|
| 8.0 | 6.0 | 0.00 | 0.4644 | 0.3577 |
| 6.0 | 6.0 | 0.00 | 0.4798 | 0.3684 |
| 4.0 | 6.0 | 0.00 | 0.4912 | 0.3914 |
| 2.5 | 6.0 | 0.00 | 0.5011 | 0.4203 |
| 4.0 | 4.0 | 0.05 | 0.4932 | 0.3945 |
| **2.5** | **4.0** | **0.05** | **0.5031** | **0.4219** |
| Nearest player, ±2 s vote | — | — | 0.3310 | 0.2250 |

The initial penalties merged too many distinct spells in development. Reducing the turnover
penalty improved spell matches. After the gap fix, the combined configuration led both
conditions, by a small margin over the same turnover penalty with the original stoppage
settings. The five-minute competition reference plays no role in this comparison.

## Consequences

A breakpoint without visible control or stoppage evidence remains uncertain. Some correctly
detected physical changes differ from the reference convention for loose or deflected balls.
The DFL data is a useful comparison across matches with stronger tracking. Its scores do not
estimate the hidden competition score. Reopen the decision with other permitted targets or a
new benchmark whose tracking loss better matches the tactical feed.
