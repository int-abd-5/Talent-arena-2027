---
chunk: 900
kind: gotchas
covers: mistakes already made and their fixes, tooling paths, conventions
session: S1
completed: '2026-11-17'
timeline: SESSIONS.md
---

# Operational Gotchas

**Read this before writing a file.** These are mistakes actually made in this project, not hypotheticals.
Add an entry the moment a mistake costs real time, with the symptom, the cause and the fix. Delete one that
turns out to be wrong.

## Seeded from experience on earlier projects

These are real failures from earlier work, kept here because the same environment produces them again.

- **Git Bash rewrites path-like arguments.** `//` arrived as `/` and a crash test tested nothing. Set
  `MSYS_NO_PATHCONV=1` for URL paths and hostile inputs.
- **Never run a patch script through an interpreter heredoc.** Backslashes and quoting corrupt it silently.
  Write the script to a file and run it by path.
- **Full test runs and a global pre-push hook can run out of memory.** Cap workers
  (`VITEST_MAX_WORKERS=4`) rather than bypassing the hook.
- **A local green can be meaningless for a clone.** CRLF copies and absolute links make a working tree pass
  what a fresh checkout fails. Verify each milestone in a fresh checkout.
- **Background servers outlive their task.** Start with `exec` so stopping the task stops the process, check
  the port is free first, and stop what you started. One ran ten hours unnoticed.
- **A killed agent reports nothing but may have written thousands of good lines.** Read the tree first.
- **An agent's closing summary can contradict its own evidence.** Check each headline count against its table.

## This project

(add the next one here)
