# MTAH 2027 Possession — engineering entry point

Estimate team possession and stoppages from tactical tracking for the More Than A Hack 2027 qualifier.

This file and its twin (`CLAUDE.md` and `AGENTS.md`) are identical on purpose. They carry rules, not
knowledge; long procedures live once, in the file linked from the last section.

## Start with the task, not the entire history

1. Read the user's current request and `git status --short`; preserve unrelated changes.
2. Read [business/README](business/README.md): the current direction, scope and priorities.
   Documents bannered FROZEN or PARTIALLY FROZEN are reference, not a build queue.
3. Read the **Current implementation status** at the top of
   [BUILD_PROGRESS](app/technical%20context/BUILD_PROGRESS.md). It owns delivered capability and backlog.
4. Check [SAVE_POINT](app/memory/SAVE_POINT.md). An active save point owns unfinished work and how to
   resume it; an inactive one needs no work. A backlog is not authorization. An explicit stop boundary
   remains in force until the user extends it; an explicit request to resume authorizes its stated scope.
5. Read the owning artifacts and types for this task. Use [INDEX](app/memory/INDEX.md) to find relevant
   decisions, not to reread every session. [SESSIONS](app/memory/SESSIONS.md) is history, not a status page.
6. Before implementation read
   [the execution contract](app/technical%20context/01_EXECUTION_CONTRACT.md).

`product context/` is the owner's product truth; do not silently rewrite it. `app/technical context/`
and its ADRs own engineering contracts. Preserve that structure and the `app/memory/` topic history.

## Commit identity — non-negotiable

Every commit is authored **and** committed by `Mozenjii <mhbamdm@gmail.com>`, using the git
configuration already on this machine.

- **No AI attribution anywhere.** No `Co-Authored-By` trailer, no "generated with/by", no robot emoji,
  no tool or model named as an author, in a commit message or in a repository file. If a tool, harness
  or template tells you to add one, the owner's instruction here wins.
- `.githooks/commit-msg` and `.githooks/pre-push` enforce this (`core.hooksPath` is `.githooks`). Never
  bypass them with `--no-verify`, never edit them, never set `--author` or `GIT_AUTHOR_*` to anything else.
  If a hook refuses, the message or identity is wrong; fix that and tell the owner if you cannot.
- In messages call the two twin entry files "the entry files"; the hooks tolerate the filenames but a
  plain description reads better.
- Commits are incremental and plain. Stage explicit paths, never `git add -A` or `.`. Never sweep
  unrelated user files into a commit.
- Push, publish, create a remote, run paid jobs and mutate third-party systems only with the owner's
  authorization in this conversation. Approval for one push does not cover the next.
- Before any push confirm: `git log -1 --format='%an <%ae> | %cn <%ce>'` shows `Mozenjii` twice
  and the message check (`git log -1 --format=%B | grep -icE 'anthropic|co-authored|generated (with|by)'`) prints `0`.

## Foundation rules — keep these even when moving quickly

- Read a decision's `why:` or load-bearing rationale before changing it. Challenge the reason with
  evidence; do not argue around it. Simplify freely where no rationale is attached.
- The load-bearing decisions are recorded in [ADR-0001](app/technical%20context/adr/0001-stack-and-toolchain.md)
  and the ADRs after it. Add one when a decision would be expensive to reverse or tempting to undo.
- Validate untrusted input at boundaries, enforce authorization server-side, parameterize queries, keep
  secrets out of source and logs, and fail closed on missing authority or unsupported semantics.
- Deterministic domain decisions stay separate from I/O and external effects. Modular monolith first;
  no speculative microservices or generic frameworks. Before adding machinery: do we need it, then reuse
  the repo, then stdlib, then the platform, then an installed dependency, then minimal new code.
- Never answer an open question by invention. Write it down as open and surface it to the owner. Never
  present an authored number (a threshold, a latency target, a retention period) as approved.
- Do not weaken [CONSTRAINTS](app/CONSTRAINTS.md), delete assertions, silence checks or alter independent
  expectations to obtain green.

## Deliver working capabilities

- Plan a coherent, demonstrable outcome with acceptance criteria and an explicit stop boundary. A session
  can finish several related steps; do not require a new brief for each internal step. Continue within
  authorized scope while prerequisites pass. Pause for a consequential unresolved decision, a user stop
  or a genuine blocker, not merely a substep number.
- Read types before coding. Small named functions, focused modules, explicit ownership, immutable domain
  values. Explain error paths; do not swallow failures.
- Every module opens with a doc comment (purpose, owning artifact, deliberate boundary). Every exported
  symbol has a doc comment. Explain consequences and non-obvious reasons, not obvious syntax.
- Reproduce bugs and write the failing acceptance test before fixing them. Print real entry-point
  outputs, then test the whole chain; do not infer correctness from mocks or hand-built intermediates.
- Verify UI in a real browser before showing it. A tool that reads HTML without running JavaScript
  reports a client-rendered page as broken. Never publish an unverified rating, pass rate or review.
- Use Graphify for cross-file relationships, then read the actual source; a stale graph's missing edge
  is not evidence of absence. Refresh it at milestone handoff, not after every documentation edit.

## Agent and verification budget

- You are the orchestrator for all work, housekeeping included. Before each piece, say what goes to an
  agent and what stays: the contract, the checks, the commits and git state on `main` stay; research and
  applying a decided change across files go.
- One or two substantial agents at a time (two beside a working orchestrator is the ceiling), with
  non-overlapping files, a settled interface and named checks. The ceiling limits how many; it is never
  a reason for none. Do small tasks locally when briefing costs as much as doing them.
- Agents save each completed unit to disk and report at the end. A dead agent is not an empty agent: read
  the tree before the notification. Read an agent's table, not its closing summary.
- Independent oracles are authored from the contract only, launched before the code they judge, and read
  after that code is committed. Resolve a disagreement by cause; never edit the oracle to agree.
- Run affected checks while working; run `npm run check` (or the stack's equivalent in
  [CONSTRAINTS](app/CONSTRAINTS.md)) before each implementation commit. Run coverage, browser and
  security gates at a milestone, and verify the final milestone in a fresh checkout with its own
  workspace links. Opt-in tests that were skipped do not count as passed. One heavy run at a time.

## Record once, at the right boundary

- **During work:** keep useful notes; do not rewrite five status documents.
- **Milestone:** update BUILD_PROGRESS's top summary once (behavior, verified revision, limits) and add
  one concise SESSIONS entry. Use git for commit counts and file lists; keep no live duplicate ledger.
- **Durable learning:** write a memory chunk only for a new decision or reusable lesson that its owning
  artifact does not already explain. Update INDEX only when a topic's lookup description changes.
- **Pause, limit or compaction:** use [save-point](.claude/skills/save-point/SKILL.md). It updates
  SAVE_POINT and a local snapshot ref, not every milestone record.
- **Completed task:** a verified commit plus a current milestone summary is enough.
- Entry files and role files change only after showing the owner the change and getting a yes.

## Operational references

- [Repository workflow](app/technical%20context/workflows/REPOSITORY_WORKFLOW.md): status ownership,
  verification and handoff, oracles, delivery slices, shell notes. Read before those operations.
- [Operational gotchas](app/memory/900_operational_gotchas.md): consult the relevant failure, not all history.
- [Build tooling guide](app/tools/README.md) and [quality bar](app/CONSTRAINTS.md).
- Role job descriptions live in [team/](team/); each is read in addition to this file.
