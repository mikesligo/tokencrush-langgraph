# Makefile for tokencrush-langraph

.PHONY: help venv install dev test build clean release run-example run-simple run-rag run-blog example-deps

help: ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sed -E 's/:.*##/: /'

.venv: ## Create virtual environment in .venv
	python3 -m venv .venv

venv: .venv ## Ensure venv exists
	@echo "Run: source .venv/bin/activate"

install: venv ## Install package in editable mode
	./.venv/bin/pip install -U pip build
	./.venv/bin/pip install -e .

dev: install ## Install dev tools (pytest, twine)
	./.venv/bin/pip install -U pytest twine

test: ## Run tests if tests/ exists
	@if [ -d tests ]; then \
		./.venv/bin/pytest -q; \
	else \
		echo "No tests directory. Skipping."; \
	fi

build: clean install ## Build sdist and wheel
	./.venv/bin/python -m build

clean: ## Remove build artifacts
	rm -rf build dist *.egg-info src/*.egg-info src/*/*.egg-info

release: build ## Upload to PyPI via twine (set TWINE_USERNAME/TWINE_PASSWORD or token)
	./.venv/bin/twine upload dist/*

run-example: ## Run examples/simple_crush.py (requires TOKENCRUSH_API_KEY env var)
	@test -n "$(TOKENCRUSH_API_KEY)" || (echo "TOKENCRUSH_API_KEY env var required" && exit 1)
	./.venv/bin/python examples/simple_crush.py

run-simple: run-example ## Alias for run-example

run-rag: ## Run pure LangGraph RAG example (requires TOKENCRUSH_API_KEY, OPENAI_API_KEY)
	@test -n "$(TOKENCRUSH_API_KEY)" || (echo "TOKENCRUSH_API_KEY env var required" && exit 1)
	@test -n "$(OPENAI_API_KEY)" || (echo "OPENAI_API_KEY env var required" && exit 1)
	./.venv/bin/python examples/rag_crush_langgraph.py

run-blog: ## Run minimal blog example (requires TOKENCRUSH_API_KEY)
	@test -n "$(TOKENCRUSH_API_KEY)" || (echo "TOKENCRUSH_API_KEY env var required" && exit 1)
	./.venv/bin/python examples/blog_minimal.py

example-deps: ## Install example dependencies (requests, bs4, openai)
	./.venv/bin/pip install -U requests beautifulsoup4 openai


