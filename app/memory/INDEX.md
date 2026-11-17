# MTAH 2027 Possession — Project Memory Index

Use this index to find durable decisions and lessons. It is not a current-status page.

- Delivered behavior, verification revision, limits and backlog:
  [BUILD_PROGRESS](../technical%20context/BUILD_PROGRESS.md), top summary.
- Active unfinished work and its resume prompt: [SAVE_POINT](SAVE_POINT.md).
- Milestone chronology: [SESSIONS](SESSIONS.md). Exact commit metadata: `git log`.
- Working rules: [CLAUDE.md](../../CLAUDE.md) / [AGENTS.md](../../AGENTS.md), with
  [operational details](../technical%20context/workflows/REPOSITORY_WORKFLOW.md) loaded on demand.

Read the relevant topic, not the entire archive. Add or update a chunk only for reusable knowledge not
already explained in the owning artifact. A chunk may span several commits or sessions. Update its row when
its lookup description changes; no row is required for each commit or stop. Historical counts and
next-step statements belong to their dated slices, not to today's state.

## Chunks

| # | Chunk | Covers | Commit |
|---|---|---|---|
| 000 | `000_project_charter.md` | What the project is, what the owner asked for, standing constraints | — |
| — | `SESSIONS.md` | **The time axis.** Every session, its span, its commits, and how it ended | — |
| 900 | `900_operational_gotchas.md` | Mistakes already made, tooling paths, conventions | — |
| 901 | `901_user_preferences.md` | How the owner wants this work done | — |

One chunk per unit of work, named `NNN_<topic>.md`, with frontmatter `chunk, kind, covers, session,
completed, timeline`. Lead with the finding, then the evidence.
