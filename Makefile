.PHONY: install test clean dev format lint help

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package in production mode
	pip install .

dev:  ## Install package in development mode
	pip install -e ".[dev]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=excelimermaid --cov-report=html --cov-report=term

format:  ## Format code with black
	black src/ tests/

lint:  ## Run linters (mypy, black check)
	black --check src/ tests/
	mypy src/

clean:  ## Remove build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

example:  ## Run example rendering
	excelimermaid examples/basic_flowchart.mmd -o output.svg
	@echo "Generated output.svg"
