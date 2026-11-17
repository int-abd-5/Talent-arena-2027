---
chunk: 000
kind: charter
covers: what the project is, what was asked, standing constraints
session: S1
completed: '2026-11-17'
timeline: SESSIONS.md
---

# Project Charter

## What MTAH 2027 Possession is

Estimate team possession and stoppages from tactical tracking for the More Than A Hack 2027 qualifier.

State the product in one sentence the owner would sign, then name what it is **not** (the adjacent things
people will assume). Add the north-star metric when there is one.

## What the owner asked for

Record the original request in the owner's words, then the instructions that followed, in the order
received. This is the chunk a context-less session reads to learn what was authorized.

## The governing constraint

Name the boundary that binds engineering: usually that the technical work **implements** the product
truth in `product context/` and does not **redefine** it. Where analysis forces a product decision, it
goes to the owner as a finding in `app/technical context/reviews/`.

## Rejection criteria

List the conditions under which any architecture or plan is rejected outright (for example: lacks an audit
trail, assumes an interface that may not exist, allows an unsupported claim). Each criterion names the file
and mechanism that defends it, so it is checkable rather than aspirational.

## Standing constraints

- Every commit is authored and committed by Mozenjii with no AI attribution; see the entry files.
- Synthetic data only until the release gates in the execution contract pass.
- Open questions stay open until the owner answers them; they are never filled by invention.

## Deliverable shape and conventions

Specifications are numbered markdown files with YAML frontmatter (`doc_id`, `depends_on`, `stability`).
Cross-reference by `doc_id`, never by file number. Machine-readable specs are fenced `yaml` blocks whose
first line is `# artifact: <ID>`. Time is Asia/Karachi (UTC+5).
