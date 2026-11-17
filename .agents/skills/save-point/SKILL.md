---
name: save-point
description: Preserve unfinished work before a usage limit, compaction, or explicit stop. Read the repository's canonical save-point procedure; preserve partial work without requiring green tests.
---

# Save point for Codex

Read and follow [the canonical procedure](../../../.claude/skills/save-point/SKILL.md).
It defines the stop, snapshot, record and resume contract for both harnesses. Maintain that file,
not a second copy here.

Codex controls: `collaboration.send_message` contacts a running agent but does not resume an idle
one; `followup_task` does. Use `list_agents` to establish current state and `interrupt_agent` after
the bounded save window. Agent IDs and transcripts may not survive a new session. Independently
check owned shell processes; never stop shared services as part of a save point.
