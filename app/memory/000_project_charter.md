---
chunk: 000
kind: charter
covers: qualifier deliverables and data boundaries
session: S1
completed: '2026-11-17'
timeline: SESSIONS.md
---

# Project Charter

STAR STRUCK needs a reproducible CSV assigning Barcelona, Athletic Club, or dead ball to each
graded tactical frame. The organizer measures possession spell F1 first and frame macro F1 second.
The Innovation Challenge and public release are separate decisions.

The owner requested a terminal clone of the official repository, a report on the challenge and
past winners, an arranged local data bundle, and implementation using the engineering scaffold.
The new submission repository is a sibling of that clone. The registered team name is
**STAR STRUCK**. The organizer's actual submission cutoff hour is open.

Reject a prediction pipeline that reads competition labels, uses manual match corrections, joins
on the broadcast timeline, or cannot regenerate its CSV. Reject any staged match assets or
prediction files. Use synthetic inputs for CI, the permitted local bundle for generation, and
public external matches for model selection. Run Git commits through the scaffold hooks.

[Project brief](../../business/README.md) ·
[Official rules](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/RULES.md)
