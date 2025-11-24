# Development Guide

This document provides guidelines for developing and contributing to the Agent Foundry CLI.

## Setup Development Environment

### Prerequisites

- Python 3.8 or higher
- pip
- git

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/AgentFoundryExamples/agentfoundry-cli.git
cd agentfoundry-cli
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in editable mode with development dependencies:
```bash
pip install -e ".[dev]"
```

This installs:
- The `agentfoundry_cli` package in editable mode
- Typer and its dependencies
- pytest for testing
- pytest-cov for coverage reporting

## Project Structure

```
agentfoundry-cli/
├── agentfoundry_cli/      # Main package directory
│   ├── __init__.py        # Package initialization and metadata
│   ├── __main__.py        # Entry point for 'python -m agentfoundry_cli'
│   └── cli.py             # Main CLI application and commands
├── tests/                 # Test directory
│   └── __init__.py        # Test package initialization
├── docs/                  # Documentation
│   └── development.md     # This file
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # User-facing documentation
└── LICENSE                # GPLv3 License
```

## Running the CLI

### Method 1: Installed Command

After installing with `pip install -e .`, use the `af` command:
```bash
af --help
af hello
af version
```

### Method 2: Python Module

Run as a Python module without installation:
```bash
python -m agentfoundry_cli --help
```

### Method 3: Direct Execution

Run the CLI file directly (useful for quick testing):
```bash
python agentfoundry_cli/cli.py --help
```

## Testing

### Running Tests

Execute all tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=agentfoundry_cli --cov-report=term-missing
```

Run specific test files:
```bash
pytest tests/test_cli.py
```

### Writing Tests

Tests should be placed in the `tests/` directory and follow these conventions:
- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test functions should be named `test_*`

Example test structure:
```python
# tests/test_cli.py
from typer.testing import CliRunner
from agentfoundry_cli.cli import app

runner = CliRunner()

def test_hello_command():
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello from Agent Foundry CLI!" in result.stdout
```

## Adding New Commands

To add a new command to the CLI:

1. Open `agentfoundry_cli/cli.py`
2. Add a new function decorated with `@app.command()`:

```python
@app.command()
def mycommand(
    arg: str = typer.Argument(..., help="Description"),
    option: bool = typer.Option(False, "--flag", "-f", help="Optional flag")
):
    """
    Brief description of what the command does.
    """
    # Implementation here
    typer.echo(f"Running mycommand with {arg}")
```

3. Test your command:
```bash
af mycommand --help
af mycommand "test"
```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

## Dependencies

### Core Dependencies
- **Typer[all]**: CLI framework with rich output and shell completion
  - Includes `rich` for beautiful terminal output
  - Includes `shellingham` for shell detection and completion

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting

### Adding New Dependencies

When adding dependencies:

1. Add to `pyproject.toml` under `[project.dependencies]` or `[project.optional-dependencies]`
2. Update documentation if the dependency affects usage
3. Test that the package still installs correctly:
```bash
pip install -e ".[dev]"
```

## Contribution Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test thoroughly

3. Commit with clear, descriptive messages:
```bash
git commit -m "Add feature X to support Y"
```

4. Push and create a pull request:
```bash
git push origin feature/your-feature-name
```

## Debugging

### Enable Verbose Output

For debugging, you can add `--verbose` flags or use environment variables:
```bash
# Example for future implementation
export AF_DEBUG=1
af run
```

### Testing in Isolation

Test the CLI in a fresh virtual environment to catch dependency issues:
```bash
python -m venv test_env
source test_env/bin/activate
pip install -e ".[dev]"
af --help
deactivate
rm -rf test_env
```

## Console Entry Point

The `af` command is registered in `pyproject.toml`:
```toml
[project.scripts]
af = "agentfoundry_cli.cli:main"
```

This tells setuptools to create a console script that calls the `main()` function in `agentfoundry_cli.cli`.

## Future Development

Areas for future enhancement:
- **Parser Features**: Implement parsing logic for agent definitions
- **Run Command**: Add `af run` for executing agent workflows
- **Configuration**: Support for config files and environment variables
- **Plugins**: Extensible plugin system for custom commands
- **Shell Completion**: Pre-configured completions for bash, zsh, fish

## Troubleshooting

### `af` command not found

Ensure the package is installed and your virtual environment is activated:
```bash
which af
pip list | grep agentfoundry
```

### Import errors

Reinstall in editable mode:
```bash
pip install -e ".[dev]"
```

### Tests failing

Ensure all dependencies are installed:
```bash
pip install -e ".[dev]"
pytest -v
```

## Resources

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Packaging Guide](https://packaging.python.org/)

## Getting Help

- Submit issues on [GitHub](https://github.com/AgentFoundryExamples/agentfoundry-cli/issues)
- Review existing documentation in `docs/` and `README.md`
