---
doc_id: EXECUTION-CONTRACT
document: Qualifier execution contract
purpose: Define inputs, output, evidence and completion for local possession inference.
stability: review
as_of: '2026-11-17'
---

# Qualifier execution contract

The [official specification](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/CHALLENGE.md)
defines possession as controlled team ownership while play is live. A brief touch can leave the
original team in possession. The algorithm must write exactly one row per tactical video frame.

## Slices and acceptance

| Slice | Finished when |
|---|---|
| B0 | A locked Python environment and repository check run unattended. Local data and generated results are ignored. |
| B1 | Synthetic tests cover a brief opponent touch, metric scale, tracking gaps, a legal turnover, a stoppage and restart, tag alignment, and invalid or missing input. |
| B2 | The official baseline is reproduced, and the decoder is selected using other games with visible and masked ball tracks. The held-out match is evaluated after selection. |
| B3 | The offline CLI regenerates the named 199,319-row CSV byte for byte from a clean checkout. The official validator accepts it. |
| B4 | The team has the CSV, technical report and source instructions. Publishing a repository and sending the form require the owner's authorization. |

Input, feature extraction, path decoding and output writing are separate functions in one local CLI.
Validate frame IDs and team mapping at ingestion. Use normalized XY on the tactical time base and
the organizer's published half boundaries. Independent QA checks behavior on synthetic inputs.
Keep results from the competition's public reference limited to one pipeline check of the frozen
entry. See the [quality gates](../CONSTRAINTS.md) and [current progress](BUILD_PROGRESS.md).
