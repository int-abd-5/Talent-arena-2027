# STAR STRUCK | More Than A Hack 2027

Generate the team's Phase 1 possession CSV from the local tactical dataset. The CLI uses Python and
NumPy and runs on a CPU. The organizer's Git repository supplies the reference validator and scorer.
See the [technical report](TECHNICAL_REPORT.md) for the method and results.

## Reproduce the submission

Start from this repository's root with Python 3.12.14 and [uv](https://docs.astral.sh/uv/). Put the
provided tactical assets under any local dataset root:

```text
data/
└── tactical/
    ├── BAR-ATH_tactical_atd.txt
    ├── BAR-ATH_tactical_atd.xml
    └── BAR-ATH_tactical_smart_tagging.xml
```

```sh
uv sync --locked
uv run --locked python -m app.possession --data-dir data --output 'outputs/STAR STRUCK.csv'
```

With the arranged dataset in a sibling organizer clone, use `--data-dir '../more-than-a-hack-2027/data'`.
The command also accepts `MTAH_DATA_DIR` when `--data-dir` is omitted.

From this repository, run the official validator with the same Python environment and a sibling clone
of the organizer repository at the inspected revision `f8f2629`:

```sh
uv run --locked python ../more-than-a-hack-2027/evaluation/validate_submission.py 'outputs/STAR STRUCK.csv'
```

The reproduction command needs only the three files above. The [public DFL benchmark](app/tools/DFL_BENCHMARK.md)
is available separately for external replication. `make check` runs synthetic coverage, repository
checks, formatting, lint and types. `make audit` checks locked runtime dependencies.

Keep the match files, working exports and possession CSVs in ignored local folders. The organizer
accepts the named CSV, a public source repository URL, and the named technical report through its
participant form. [Submission instructions](https://github.com/metrica-sports/more-than-a-hack-2027/blob/f8f2629/SUBMISSION.md)
