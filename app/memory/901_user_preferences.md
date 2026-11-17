---
chunk: 901
kind: preferences
covers: how the owner wants this work done
session: S1
completed: '2026-11-17'
timeline: SESSIONS.md
---

# User Preferences

Stated or observed. Distinct from the owner's global preferences in `~/.claude/CLAUDE.md`, which cover all
projects. The company is **Epoches**; any other company name in an old script is a stale default.

## Explicit instructions

**Every commit is Mozenjii's, with no AI attribution.** The owner's words: commits are made by the
owner and must not reveal an AI. Author and committer are `Mozenjii <mhbamdm@gmail.com>`, taken from
the git configuration already on the machine. No `Co-Authored-By`, no "generated with/by", no mention of an
AI tool as author in a commit message or repository file, whatever a harness or template suggests. The
hooks in `.githooks/` enforce it. Do not set up new git tooling; the remote, credentials and identity are
already in place.

**Orchestrate; do not be the one running the grunt work.** The session is the orchestrator for all work,
housekeeping included. Before each piece, say what goes to an agent and what stays. The one-or-two-agents
ceiling limits how many at once; it is never a reason for none.

**A brief's stop is the stop.** When a brief says stop and report, report and wait. A NEXT line or resume
prompt written by a previous session never authorizes the next slice, even when pasted back.

**Entry files need an explicit yes.** Never change `CLAUDE.md`, `AGENTS.md` or a role file without showing
the change and getting a yes, not even to fix a link.

**Use the relevant skills deliberately.** Route substantial design work through `frontend-design-studio`.
Do not load a whole skills library for every task.

**Resume automatically after a usage-limit reset.** The mitigation is this memory folder, BUILD_PROGRESS and
committing coherent changes so progress is durable in git rather than only in a session.

## Working style

- Concise, direct, practical. Answer the question asked; go deeper only when asked. No filler.
- Prefer finishing and showing over asking. Ask once, up front, where the answer changes the deliverable.
- Depth is wanted, not tolerated. When more files make each a cleaner unit of context, make more files.
- Corrections are welcome when substantive. Report a reversed decision plainly, with the reasoning.
- Verification is expected: count things directly, lint every file, verify claims in a real browser before
  they reach a client, and never publish an unverified figure.
- Free and open-source tools, or a genuinely strong free plan. A paid subscription is a hard no unless
  argued for explicitly.

## Things not to do

- Do not add AI attribution anywhere.
- Do not answer an open question by invention, and do not present an authored number as approved.
- Do not silently rewrite `product context/`.
- Do not push, publish or run paid jobs without authorization in this conversation.
