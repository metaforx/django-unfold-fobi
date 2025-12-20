.PHONY: install lint test clean build

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

lint:
	@echo "Running linters..."
	@if command -v black >/dev/null 2>&1; then \
		black --check src/; \
	else \
		echo "black not installed, skipping..."; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort --check-only src/; \
	else \
		echo "isort not installed, skipping..."; \
	fi
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/; \
	else \
		echo "flake8 not installed, skipping..."; \
	fi

test:
	@echo "Running tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest; \
	else \
		echo "pytest not installed, skipping tests..."; \
	fi

build:
	hatch build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

