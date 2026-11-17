# Toolchain: not chosen yet

This repository was scaffolded with `--stack none`. No language toolchain, check command or CI exists.

B0's first task, before any product code:

1. Choose the language, runtime, type and lint tooling, test runner and coverage tool. Record the choice in
   [ADR-0001](technical%20context/adr/0001-stack-and-toolchain.md) with alternatives and a revisit trigger.
2. Create the workspace, a lockfile and a pinned runtime.
3. Fill the "Enforced with numbers" table in [CONSTRAINTS](CONSTRAINTS.md): one row per dimension, each
   naming its command, when it runs and why. One command, `check`, runs the cheap gates in order.
4. Add `.github/workflows/ci.yml` mirroring that command, with a header listing what is not gated yet.
5. Watch each gate fail once on a deliberate bad input, then delete this file.
