.PHONY: help install test lint check shellcheck version clean

SHELL := /usr/bin/env bash

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the fablize skill into Hermes
	bash setup/setup.sh --skill-only

install-local: ## Install skill + inject block into ./AGENTS.md
	bash setup/setup.sh --local

install-global: ## Install skill + inject block into ~/.claude/CLAUDE.md
	bash setup/setup.sh --global

uninstall: ## Uninstall the fablize skill
	bash setup/uninstall.sh --all

test: ## Run tests with pytest
	python3 -m pytest tests/ -v --tb=short

lint-py: ## Lint Python files with ruff
	@which ruff >/dev/null 2>&1 && ruff check scripts/ tests/ || \
		echo "ruff not installed — run: pip install ruff"

check-py: ## Type-check Python files
	@which mypy >/dev/null 2>&1 && mypy scripts/ tests/ || \
		echo "mypy not installed — run: pip install mypy"

shellcheck: ## Check shell scripts syntax
	@ok=true; \
	for sh in setup/*.sh; do \
		bash -n "$$sh" && echo "  ✓ $$sh" || { ok=false; echo "  ✗ $$sh"; }; \
	done; \
	$$ok

check: lint-py shellcheck ## Run all checks

version: ## Show project version
	@cat VERSION

clean: ## Remove cache and temporary files
	rm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache
	rm -rf *.egg-info .coverage htmlcov
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
