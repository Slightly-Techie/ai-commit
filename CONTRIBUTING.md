# Contributing to ai-commit

Thank you for your interest in contributing! We welcome bug reports, feature requests, and pull requests.

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Slightly-Techie/ai-commit
    cd ai-commit
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows, use: .venv\Scripts\activate
    ```

3.  **Install dependencies in editable mode:**
    We use `uv` (or `pip`) for dependency management. This command installs the project itself and all development tools like `pytest` and `ruff`.
    ```bash
    pip install uv
    uv pip install -e '.[dev]'
    ```

## Running Tests and Linting

We follow a strict Test-Driven Development (TDD) workflow. All code must pass linting and testing checks.

1.  **Run the test suite:**
    This includes unit and integration tests.
    ```bash
    pytest
    ```

2.  **Check for at least 90% test coverage:**
    ```bash
    pytest --cov=ai_commit --cov-fail-under=80
    ```

3.  **Run the linter:**
    We use `ruff` for linting and code style enforcement.
    ```bash
    ruff check .
    ```

## Submitting a Pull Request

1.  Fork the repository.
2.  Create a new branch for your feature or bugfix.
3.  Write your code, including tests that cover your changes.
4.  Ensure all tests and linting checks pass.
5.  Push your branch and open a pull request.