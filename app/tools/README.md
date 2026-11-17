# The build tooling, for whoever maintains it next

Everything under `app/tools/` is build-time: it checks, generates or judges, and none of it ships. Read this
before changing any of it, then read the module header of the file you are changing; every one says what it
is for and what it deliberately does not do.

## Packages

| Package | What it does | Why it is separate |
|---|---|---|

Add a row per package. An oracle package must import nothing from the code it judges, declare no
dependency on it and hold no implementation of what it judges; say so in its row.

## The rules that will bite you

**Never hand-edit generated output.** Fix the specification or the generator, then regenerate.

**A generator that cannot satisfy its artifact throws.** No placeholder, no TODO, no permissive default.
Emitting something provisional so downstream code compiles is the exact failure this rule exists to prevent.

**Order in an artifact is behaviour, not presentation.** Read numbered `order` keys; never restate them as a
chain of checks that happens to agree today.
