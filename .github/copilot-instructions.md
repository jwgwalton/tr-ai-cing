# GitHub Copilot Instructions

## Python Package Management

This project uses `uv` as the Python package manager. When working with dependencies:

- Use `uv add <package>` to add packages to the project
- Use `uv add --dev <package>` to add development dependencies
- Use `uv venv` to create a virtual environment
- Use `uv pip install -e ".[dev]"` to install the project in development mode with dev dependencies
- Use `uv run <command>` to run commands in the project's virtual environment

## Testing

This project uses `pytest` for testing. When running tests:

- Use `uv run pytest` to run all tests
- Use `uv run pytest -v` for verbose output
- Use `uv run pytest <test_file>` to run specific test files
- Use `uv run pytest --cov=tracing` to run tests with coverage

## Development Workflow

1. Create virtual environment: `uv venv`
2. Install dependencies: `uv pip install -e ".[dev]"`
3. Run tests: `uv run pytest -v`
4. Run tests with coverage: `uv run pytest --cov=tracing --cov-report=html`
