---
name: save-point
description: Preserve unfinished work before a usage limit, compaction, or explicit stop. Quiesce known writers, record one active handoff, and snapshot reviewed paths locally without changing the real index or requiring green tests.
---

# Save point

Use for unfinished work when the user requests a save point or a limit/compaction is near.
A completed task with a normal milestone handoff needs no save point. Stopping a chat alone
does not guarantee that background agents or processes stop, or that context survives compaction.

## One record for each purpose

- `app/technical context/BUILD_PROGRESS.md`: authoritative delivered capabilities and ordered backlog.
- `app/memory/SAVE_POINT.md`: only active unfinished work, replaced at each stop.
- `app/memory/SESSIONS.md`: chronological milestone history and stable navigation links.
- Topic memory: new durable decisions and causes worth preserving, not repeated progress counts.

A stop updates only `SAVE_POINT.md` and the local snapshot ref. No ledger, index, graph or gbrain
update is required. Normal completed milestones still follow the repository's verification and
handoff rules. Do not invent a memory-only exception to pre-commit checks.

## Stop safely

1. Announce the save point, start nothing new, and inventory known agents and shell tasks.
2. Ask running agents to save partial work and report (message below). Preserve independent briefs
   verbatim, either in the record or at a durable path included in the snapshot. Do not rewrite a
   brief after reading the implementation it independently judges.
3. Allow a bounded wait (up to a minute at a time, a few minutes total if budget permits). Interrupt
   remaining known workers using the harness's supported controls. Preserve files as found and mark
   them PARTIAL. Stop only this task's owned processes, never a shared service or an unknown process.
4. Inspect disk changes and reports. Record completeness separately from correctness. Do not require
   tests, formatting, commits or a valid intermediate source file to rescue unfinished work.
5. Write `app/memory/SAVE_POINT.md`, review snapshot candidates, then snapshot after writers are quiet.
   Keep unrelated user changes untouched; include them only after review or explicitly record their
   exclusion and ownership. Never blindly include ignored files, credentials, PHI or secret-bearing
   configuration. If durable preservation is unresolved, say so rather than claiming safety.
6. Check the selected paths against the snapshot and inspect status again for newly created paths.
   If anything changed, update the record and snapshot again. Report the ref/hash and whether it is
   safe to compact. A ref snapshot is sufficient rescue; no branch commit or full check is required.

**Safe to compact** means known writers are stopped and every task-owned continuation input is
captured or verified durable elsewhere, including distinct staged content. Unrelated exclusions
must identify their untouched owner. Listing missing required context is not preserving it: missing
inputs, an unstopped writer or unknown process state mean **not yet safe**. Green code is not required.

If only seconds remain: send stop requests, write a minimal record, and take a provisional snapshot
of reviewed paths. Mark writers and completeness unknown; do not claim quiescence. When possible,
follow with the normal final snapshot after writers stop. Never revert work to manufacture safety.

## Agent message

```text
SAVE POINT: start no new work. Save your current partial work to your owned files now.
Do not revert unfinished/shared edits, stage, commit, stash, reset or check out files.
Write a short progress note at <owned note path>: completed units, partial units,
remaining steps, checks actually run and their outcomes, and processes still running.
Skip new checks if time is short. Reply with what is on disk and then stop.
```

## Local snapshot (Git Bash)

First inspect `git status --short --untracked-files=all` and the diffs. Review file contents where
needed without printing secrets. Replace the example `paths` array with explicitly approved paths,
including the save-point record and any agent notes/briefs. List individual files where a directory
could contain unrelated work. Deleted tracked paths may be listed too. Do not use `.` or `add -A`.

Run the entire block as one script. The subshell and temporary index protect the caller's index
and environment; failure aborts before the ref moves. This makes a local commit object, not a
branch commit. It must not be pushed.

```bash
(
  set -euo pipefail
  cd "$(git rev-parse --show-toplevel)"
  paths=('app/memory/SAVE_POINT.md' 'replace-with-reviewed-path')
  head=$(git rev-parse HEAD)
  prev=$(git rev-parse --verify -q refs/wip/save-point || true)
  temp_dir=$(mktemp -d)
  trap 'rm -f "$temp_dir/index" "$temp_dir/index.lock" "$temp_dir/staged.patch"; rmdir "$temp_dir"' EXIT
  test -z "$(git ls-files --unmerged)"
  git diff --cached --binary --full-index "$head" -- "${paths[@]}" > "$temp_dir/staged.patch"
  export GIT_INDEX_FILE="$temp_dir/index"
  git read-tree "$head"
  staged_snap=''
  if [ -s "$temp_dir/staged.patch" ]; then
    git apply --cached --binary "$temp_dir/staged.patch"
    staged_tree=$(git write-tree)
    staged_snap=$(git commit-tree "$staged_tree" -p "$head" -m 'Save reviewed staged work')
  fi
  git read-tree "$head"
  git add -- "${paths[@]}"
  tree=$(git write-tree)
  parents=(-p "$head")
  if [ -n "$prev" ]; then parents+=(-p "$prev"); fi
  if [ -n "$staged_snap" ]; then parents+=(-p "$staged_snap"); fi
  snap=$(git commit-tree "$tree" "${parents[@]}" -m 'Save unfinished work')
  test "$(git rev-parse HEAD)" = "$head"
  git read-tree "$head"
  git add -- "${paths[@]}"
  test "$(git write-tree)" = "$tree"
  git update-ref refs/wip/save-point "$snap" "$prev"
  printf 'Snapshot: %s\n' "$snap"
  printf 'Reviewed staged snapshot: %s\n' "${staged_snap:-none}"
  git diff --stat "$head" "$snap"
)
```

Parent order is HEAD, previous snapshot if present, then staged snapshot if present. Only reviewed
paths enter the staged parent; unrelated index changes are not retained. The explicit unmerged-index
check refuses conflicts: preserve the conflict files separately and report incomplete rescue rather than
claiming this command succeeded. Record the printed staged hash if present; its parent is HEAD.
The prior snapshot parent retains history. The old-value check refuses a concurrent ref update.
Inspect status afterwards: tree equality covers selected paths, not an unlisted new file. Snapshots
preserve Git content, not ignored runtime state or secrets. The real index stays untouched.
Use `git show refs/wip/save-point:app/memory/SAVE_POINT.md` to recover the record if needed
Inspect a diff before restoring an individual path; use the staged snapshot as the source to recover its
distinct version. Never restore over newer work automatically.

## Record template

```markdown
# Active save point — <date/time/timezone>
- Original task and acceptance criteria: <scope or durable reference>
- Out of scope: <boundaries>
- HEAD: <hash from git>; last verified revision: <hash, commands and actual results>
- Snapshot: refs/wip/save-point (resolve the hash with git; this record is inside it)
- Included paths: <reviewed paths>; exclusions: <paths, ownership, preservation status>
- Finished units: <...>; partial/unverified units: <...>
- Remaining steps in order: <concrete continuation>
- Agents and owned processes: <IDs, roles, state, notes/log paths; unknowns explicit>
- Independent briefs: <verbatim text or snapshotted references>
- Safe to compact: <yes/no and reason>
- Resume: Read this record and BUILD_PROGRESS. Inspect git status and snapshot differences
  before restoring anything. Continue the original scope from the remaining steps above.
```

Print a short resume prompt and the snapshot hash to the user. Do not put the new snapshot's hash
inside the record it snapshots: that would immediately make the record differ from the snapshot.

## Resume and retire

Read the record, inspect disk and establish whether any old worker still exists before launching a
successor. Agent IDs/transcripts are not guaranteed to survive a new session. Seed a successor with
the saved scope and original independent brief. Preserve newer changes when reconciling snapshots.

Retain the snapshot ref by default. Mark the record inactive only after every saved path is landed
or explicitly resolved, including pre-existing and untracked work. Any later retirement of the ref
must account for its parent snapshots too; deleting the ref is not routine cleanup. An inactive
record may point to the resolution milestone without repeating its status or test counts.

## Harness controls

- Claude: use the agent/message/task controls actually exposed in the current session. Do not assume
  an old ID can be resumed or that a message stops a worker; verify its reported state.
- Codex: `collaboration.list_agents`, `send_message`, and `interrupt_agent` manage known agents.
  `send_message` does not restart an idle agent; `followup_task` does. Check availability on resume.
  Shell processes need their own supported session controls; interrupting an agent is not proof
  that its detached processes stopped.
