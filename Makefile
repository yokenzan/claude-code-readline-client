# Makefile for Claude Code Readline Client (CCRC)

# Virtual environment setup
VENV_PATH = .venv
PYTHON = $(VENV_PATH)/bin/python
PIP = $(VENV_PATH)/bin/pip
UV = $(shell which uv)

# Project directories
SRC_DIR = ccrc
TEST_DIR = ccrc/tests

# Linting and formatting tools
BLACK = $(VENV_PATH)/bin/black
FLAKE8 = $(VENV_PATH)/bin/flake8
MYPY = $(VENV_PATH)/bin/mypy
PYTEST = $(VENV_PATH)/bin/pytest

.PHONY: help lint format check test clean setup

help:
	@echo "Available targets:"
	@echo "  format    - Format code with black"
	@echo "  lint      - Run linter (flake8) on source code"
	@echo "  check     - Run both formatter and linter"
	@echo "  test      - Run tests with pytest"
	@echo "  clean     - Remove build artifacts and cache"
	@echo "  setup     - Set up development environment"
	@echo "  help      - Show this help message"

# Format code with black
format:
	@echo "Running black formatter..."
	$(BLACK) $(SRC_DIR)/

# Run linter (flake8)
lint:
	@echo "Running flake8 linter..."
	$(FLAKE8) $(SRC_DIR)/

# Run both formatter and linter
check: format lint
	@echo "Code formatting and linting complete."

# Run tests
test:
	@echo "Running tests..."
	$(PYTEST) $(TEST_DIR)/ -v

# Clean up build artifacts
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

# Set up development environment
setup:
	@echo "Setting up development environment..."
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "Creating virtual environment..."; \
		$(UV) venv; \
	fi
	@echo "Installing dependencies..."
	$(UV) pip install -e ".[dev]"
	@echo "Development environment ready!"