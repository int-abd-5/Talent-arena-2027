# ADR-0001 | Python and NumPy on CPU

**Status** Accepted for the qualifier on 17 November 2026.

## Context

The reference repository exposes Python loaders and a NumPy and pandas scorer. The tactical
bundle is small as numeric tracking but includes two large videos. Organizers need an inspectable
one-command reconstruction of the CSV.

## Decision

Use Python 3.12.14 and one runtime library, NumPy, pinned by `uv.lock`. Read the tracking file
line by line into compact float32 arrays and infer one tactical half at a time. Use Ruff, mypy,
pytest and coverage for the reproducible local gate. Keep pandas in the development group for the
organizer's scorer, and run the pinned runtime dependency audit separately. The GitHub workflow
runs the same local commands using synthetic inputs.

## Alternatives

The scaffold's TypeScript stack would need a second environment for the organizer's tools and
duplicate numeric helpers. A full computer vision stack would enlarge the runtime and depend on
decoding or detector throughput. A notebook would assist exploration but add a second execution
path to reproduce. The CLI keeps one run command and no network requirement during inference.

## Revisit trigger

Revisit if decoded video features show measured improvement on permitted other games or if a
new target competition requires streaming inference. Keep the synthetic and official format checks.
