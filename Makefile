.PHONY: check audit

check:
	uv run --locked python -m app.tools.check_workspace
	uv run --locked ruff check app
	uv run --locked ruff format --check app
	uv run --locked mypy -p app.possession
	uv run --locked python -m pytest --cov=app.possession --cov-report=term-missing --cov-fail-under=80

audit:
	@set -eu; mtah_audit_file=$$(mktemp); trap 'rm -f "$$mtah_audit_file"' EXIT; \
	  uv export --locked --no-dev --no-emit-project --output-file "$$mtah_audit_file" --quiet; \
	  uv run --locked pip-audit --disable-pip --require-hashes -r "$$mtah_audit_file"
