# GitHub Copilot Instructions

## Python Package Management

This project uses `uv` as the Python package manager. When working with dependencies:

- Use `uv add <package>` to add packages to the project
- Use `uv add --dev <package>` to add development dependencies
- Use `uv sync` to install all dependencies
- Use `uv sync --extra dev` to install all dependencies including dev dependencies
- Use `uv run <command>` to run commands in the project's virtual environment

## Testing

This project uses `pytest` for testing. When running tests:

- Use `uv run pytest` to run all tests
- Use `uv run pytest -v` for verbose output
- Use `uv run pytest <test_file>` to run specific test files
- Use `uv run pytest --cov=tracing` to run tests with coverage

## Development Workflow

1. Install dependencies: `uv sync --extra dev`
2. Run tests: `uv run pytest -v`
3. Run tests with coverage: `uv run pytest --cov=tracing --cov-report=html`
