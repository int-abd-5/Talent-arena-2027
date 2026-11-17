# Repository workflow

The on-demand operational companion to the entry files. It is not a second current-status page.
Product and engineering contracts remain in their owning documents.

## Status ownership

| Information | Owner | Update trigger |
|---|---|---|
| Delivered behavior, verification revision, release limits and backlog | BUILD_PROGRESS top summary | Completed milestone or material correction |
| Unfinished work, authorized scope, processes, agents, restore instructions | memory/SAVE_POINT.md | Pause, limit or compaction with work in flight |
| When a milestone happened | memory/SESSIONS.md | One concise milestone entry |
| Reusable decision or debugging lesson | Owning artifact or an existing memory topic | New knowledge, written once |
| Topic discovery | memory/INDEX.md | A topic added or materially changed |
| Exact commits, timestamps and changed files | git log | Automatic |
| Cross-file traversal | graphify-out/ | Code or contract milestone |

Historical sections and existing ledgers remain evidence: label them, do not rewrite them to match
today. New milestones need no manually counted commit ledger. Do not create a follow-up commit just to
count the preceding documentation commit.

## Verification and handoff

During implementation run focused tests, then the complete check before each coherent implementation
commit. At milestone completion run coverage (80% floor), browser tests, the relevant integration and
security checks, and a **fresh-checkout verification** against the actual target revision: a disposable
worktree with its own workspace links, confirming every link resolves inside that checkout and not in
`main`. Clean up by unlinking a verified junction itself, never by following it into `main`. A failed
check never authorizes cleanup of unsaved work.

Documentation-only changes require their affected checks; artifacts consumed by generators are
implementation changes even if their filenames end in `.md`.

At handoff read BUILD_PROGRESS's summary as a newcomer: what works, what was tested at which revision,
what remains disabled, and what is authorized next. Add one history link in SESSIONS. Do not copy the same
counts, backlog or test transcript into every memory surface.

## Independent oracles and the failure shapes they find

For any module that carries rules, a separate agent authors expected results from the **contract only**,
importing nothing from the implementation. Launch it before you write what it judges, and read it only
after yours is committed, so independence is physical rather than promised. Wire a differential between
the two. Resolve each disagreement by cause: correct the artifact and regenerate, never edit the oracle to
match. A recorded disagreement is a measurement, not a guard; it keeps a defect visible but does not stop it.

Check these shapes explicitly, because each has already shipped as a defect elsewhere:

- **A partial enum fails permissively.** The artifact lists N cases, the code implements fewer, and the
  missing branch takes the approving answer instead of an error.
- **An input read in one branch is unread in the rest.**
- **Two authors of one contract agree on its holes.** After a differential agrees, review each rule against
  its own `why` for other paths to the outcome it refuses.
- **A failure count says nothing about the number of causes.** One defect can fail most of a first run.
- **A refusal that names its blocker can be retired; one that says "too hard" never is.**
- **A recorded claim that never executes has no mechanism checking it.** "The spec does not say X" needs
  a second reader; a differential verifies cases and cannot touch a gap list.

Execute generated output (DDL, config, code) through its real consumer, including the next stage of the
pipeline and a real browser where a person is the consumer. Reading it finds none of these.

## Working notes

- One heavy suite at a time. Use commands with checked exit status and retain the test's exit code, not
  `tail`'s. Avoid clever shell chains for verification, snapshotting and cleanup. Use file-based patch
  scripts rather than interpreter heredocs, preserve line endings, and assert exact matches before writes.
- Never loosen an assertion or hide an earlier failure to obtain green. Preserve failed-run evidence and
  fix the cause before rerunning.
- Start background servers so that stopping the task stops the process, check the port is free first,
  and stop what you started when done.
- Windows: PowerShell 5.1 has no `&&` and uses a backtick for line continuation; Git Bash is available
  for POSIX scripts. Git Bash rewrites path-like arguments, so set `MSYS_NO_PATHCONV=1` for URL paths.
- Cap test workers if full runs run out of memory (for example `VITEST_MAX_WORKERS=4`), never `--no-verify`.

## Delivery

Slices, their scope and exit criteria are in the [execution contract](../01_EXECUTION_CONTRACT.md). A
session plans a coherent, demonstrable outcome with acceptance criteria and a stop boundary, and reports
there. A backlog is not authorization to start it.
