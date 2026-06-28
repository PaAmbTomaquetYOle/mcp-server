.PHONY: test test-cov lint

test:
	uv run pytest

test-cov:
	uv run pytest --cov --cov-report=term-missing --cov-report=html
