---
doc_id: BUILD-PROGRESS
document: Build progress and submission handoff
purpose: Own implementation status and verification evidence.
as_of: '2026-11-17'
---

# Build progress

## Current implementation status

The offline CLI generates the full STAR STRUCK possession CSV from the tactical tracking and
automatic tags. The method, sources and reproduction instructions are in the
[technical report](../../TECHNICAL_REPORT.md). Only local dataset paths are needed.

| Slice | Outcome |
|---|---|
| B0 | Python 3.12.14 and NumPy locked. The local check and audit run. A workflow is defined for GitHub CI. |
| B1 | Geometry, motion, tags and temporal decoding implemented. Synthetic tests pass with 94.25% coverage. |
| B2 | Official baseline reproduced byte for byte. Development and external holdout checks complete. |
| B3 | The organizer's validator accepted the named 199,319-row CSV. A clean checkout at `ce15511` reproduced it byte for byte. |
| B4 | Team-named CSV and technical report available locally under the ignored outputs directory. |

The [validation record](reviews/2026-11-17-qualifier-validation.md) owns the evidence and
limitations. The local source repository has no remote. Publishing it and using the submission
form require the owner's authorization. The exact cutoff hour remains open.
