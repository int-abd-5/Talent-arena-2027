# Architecture decision records

The numbered specifications in `technical context/` stay technology-agnostic. Technology choices still
have to be made, so they live here: dated, argued, and each carrying a **revisit trigger**. That keeps
the commitment honest. A decision with no stated condition for reopening it is not a decision, it is an
assumption that has stopped being examined.

## How to read one

Every record has the same sections. The two that matter most are the last two.

**Alternatives considered** is not a courtesy list. A future reader who does not know why the obvious
option was rejected will reintroduce it.

**Revisit trigger** is the condition under which the decision should be reopened. It is a fact about the
world, not a date. "When the managed service's p95 exceeds our budget" is a trigger; "in six months" is not.

## Status vocabulary

| Status | Meaning |
|---|---|
| `proposed` | Argued and written down, not yet ratified by a build that depends on it |
| `accepted` | In force; code is expected to conform |
| `superseded` | Replaced; names its successor and stays as history |

## Index

| ADR | Decision |
|---|---|
| [0001](0001-stack-and-toolchain.md) | Stack and toolchain |

Use [TEMPLATE](TEMPLATE.md) for the next one. Number sequentially; never renumber.
