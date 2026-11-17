# MTAH 2027 Possession

Estimate team possession and stoppages from tactical tracking for the More Than A Hack 2027 qualifier.

## What is here

| Path | What it is | Who owns it |
|---|---|---|
| `business/` | Current direction on one page, plus numbered detail and `research/`. | Mohib |
| `product context/` | The product truth. **Not the agent's to rewrite.** | Mohib |
| `team/` | One folder per role agent, each with its own job description. | Mohib |
| `app/` | Everything engineering: the toolchain, `CONSTRAINTS.md` and the folders below. | Engineering |
| `app/technical context/` | Numbered specifications, `adr/`, `reviews/`, `workflows/`, `BUILD_PROGRESS.md`. | Engineering |
| `app/memory/` | Project memory chunked by topic. `SESSIONS.md` is the time axis. | Engineering |
| `app/tools/` | Build-time packages. Never ship. `app/tools/README.md` is the maintainer's guide. | Engineering |
| `app/packages/` | Runtime packages. | Engineering |
| `.claude/skills/`, `.agents/skills/` | Agent skills (`save-point`). | Engineering |
| `.githooks/` | Commit-identity and attribution gates; `core.hooksPath` points here. | Mohib |

Read `app/memory/SESSIONS.md` when resuming, `app/memory/INDEX.md` when learning the project, and
`app/technical context/01_EXECUTION_CONTRACT.md` before writing code.

## Running the checks

See [CONSTRAINTS](app/CONSTRAINTS.md) for the bar and for the command behind every row. The one
command that runs the unattended gates, cheapest first, is `npm run check` from `app/`.

## Commits

Every commit shows `Mozenjii <mhbamdm@gmail.com>` as author and committer and carries no AI
attribution. The hooks in `.githooks/` enforce it; run `git config core.hooksPath .githooks` once in a
fresh clone.
