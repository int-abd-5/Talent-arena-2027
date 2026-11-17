# Constraints

The [execution contract](technical%20context/01_EXECUTION_CONTRACT.md) specifies what the
engineering gates cover. [Build progress](technical%20context/BUILD_PROGRESS.md) records measured
results.

| Dimension | Gate | When |
|---|---|---|
| Entry files, links and public repository scope | `uv run --locked python -m app.tools.check_workspace` | `make check` and CI |
| Lint and formatting | `ruff check app` and `ruff format --check app` | `make check` and CI |
| Types | `mypy -p app.possession` | `make check` and CI |
| Unit and end-to-end synthetic data | `python -m pytest`, including the independent possession oracle | `make check` and CI |
| Statement coverage | 80% of `app.possession` with `pytest-cov` | `make check` and CI |
| Known vulnerabilities in the runtime lock | `make audit` queries the advisory service | Local handoff and CI |
| Output format and byte identity | Official validator and regeneration from a clean checkout | Once per submission revision locally |
| Commit identity | Scaffold hooks and verify-identity script | Local commits and handoff |

The local audit exposes package names and versions to the advisory service. Inference reads only
the supplied paths and writes the specified CSV. CI has no competition data. Keep validation
expectations independent, preserve the twin entry files, do not silence checks, and keep
generated assets and credentials out of tracked paths.

Browser, accessibility and latency budgets apply only if a user interface is ever built.
