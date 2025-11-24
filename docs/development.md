# Development Guide

**Version: 1.1.0**

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
│   ├── cli.py             # Main CLI application and commands
│   └── parser.py          # Tokenizer-driven .af file parser
├── tests/                 # Test directory
│   ├── __init__.py        # Test package initialization
│   ├── test_cli.py        # CLI command tests
│   ├── test_cli_run.py    # Run command integration tests
│   └── test_parser.py     # Parser and tokenizer tests
├── docs/                  # Documentation
│   ├── development.md     # This file
│   ├── format.md          # .af file format specification
│   └── usage.md           # Usage guide
├── pyproject.toml         # Project metadata and dependencies
├── README.md              # User-facing documentation
└── LICENSE                # GPLv3 License
```

## Parser Architecture

### Overview

The .af file parser uses a **tokenizer-driven state machine** architecture for robust handling of UTF-8 input, size validation, and backwards-compatible v1.0 syntax.

### Architecture Components

#### 1. Tokenizer (`Tokenizer` class)

The tokenizer performs character-by-character scanning of input and emits tokens with precise position tracking:

**Token Types:**
- `KEY` - Identifier before colon (e.g., `purpose`, `vision`)
- `COLON` - The `:` separator
- `STRING` - Quoted string values (single or double quotes)
- `LBRACKET` / `RBRACKET` - List delimiters `[` and `]`
- `COMMA` - List item separator `,`
- `COMMENT` - Comments from `#` to end of line
- `NEWLINE` - Line breaks (`\n` or `\r\n`)
- `EOF` - End of file marker

**Features:**
- Character-by-character scanning with lookahead
- Line and column position tracking for each token
- Escape sequence handling (`\"`, `\'`, `\\`, `\n`, `\t`)
- UTF-8 support including emojis and combining characters

#### 2. State Machine Parser (`Parser` class)

The parser consumes tokens from the tokenizer to build the flat `.af` structure:

**Parsing States:**
- Skip comments and newlines
- Parse key-value pairs
- Validate key names against required set
- Check for duplicate keys
- Parse string values (for `purpose`, `vision`)
- Parse list values (for `must`, `dont`, `nice`)

**Validation:**
- All required keys present
- No duplicate keys (case-insensitive)
- No unknown keys
- String values are quoted and non-empty
- List values are bracketed and non-empty
- Maintains canonical key order

#### 3. Input Loading (`load_input` function)

Centralized input loading with strict validation:

**Size Limits:**
- Maximum input size: 1MB (1,048,576 bytes)
- Files checked before reading
- Streams checked during reading
- Clear error messages on rejection

**Encoding:**
- UTF-8 required
- BOM automatically stripped if present
- UnicodeDecodeError caught and reported

### Design Guarantees

1. **Deterministic**: Same input always produces same output
2. **Position Tracking**: Every error includes line and column numbers
3. **Size Safety**: 1MB limit prevents resource exhaustion
4. **No Eval/Exec**: Pure parsing, no code execution
5. **Fixed Output Shape**: Always produces the same 5 keys in canonical order

### Error Reporting

Errors include precise location information:
```
File 'example.af', line 5, column 12: Unknown key 'invalid'
```

This enables developers to quickly locate and fix issues.

### Backwards Compatibility

The tokenizer/parser maintains full v1.0 compatibility:
- Single-line key-value syntax
- Quoted strings (single or double quotes)
- Bracketed lists with comma-separated quoted items
- Comments starting with `#`
- Case-insensitive keys normalized to lowercase

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

The project has comprehensive test coverage with 142 tests covering all core functionality.

### Running Tests

Execute all tests with pytest:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=agentfoundry_cli --cov-report=term-missing
```

Run specific test files:
```bash
pytest tests/test_cli.py
pytest tests/test_parser.py
pytest tests/test_cli_run.py
```

Run tests matching a pattern:
```bash
pytest -k "test_run_command"
```

### Test Coverage

Current test suite includes:
- **CLI commands**: Testing all CLI commands (run, version, help, hello)
- **Parser validation**: Testing `.af` file parsing logic with tokenizer
- **Tokenizer**: Token generation, position tracking, escape sequences
- **UTF-8 support**: Emojis, combining characters, BOM handling
- **Size limits**: 1MB enforcement for files and stdin
- **Error handling**: Testing all error scenarios with precise messages
- **Integration tests**: End-to-end workflow validation
- **Edge cases**: Empty files, large files, different encodings, line endings

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

## Version Management

### Version Synchronization

The project version must be kept in sync across multiple files to prevent release confusion:

**Required files to update:**
1. `pyproject.toml` - `version` field under `[project]`
2. `agentfoundry_cli/__init__.py` - `__version__` variable

**Example update process:**
```bash
# Update version in pyproject.toml
# version = "X.Y.Z"

# Update version in agentfoundry_cli/__init__.py
# __version__ = "X.Y.Z"

# Verify the version is correct
af version
```

### Versioning Guidelines

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR version (X.0.0)**: Incompatible API changes
- **MINOR version (0.X.0)**: New functionality in a backward-compatible manner
- **PATCH version (0.0.X)**: Backward-compatible bug fixes

### Release Process

When preparing a new release:

1. **Update version numbers** in both `pyproject.toml` and `agentfoundry_cli/__init__.py`
2. **Update CHANGELOG.md** with the new version section:
   - Document new features, changes, fixes, etc.
   - Add release date
   - Update version history links
3. **Update documentation** if needed:
   - README.md version references
   - Documentation version headers if significant changes
4. **Run tests** to ensure no regressions:
   ```bash
   pytest -v
   ```
5. **Verify CLI version** command returns correct version:
   ```bash
   af version
   ```
6. **Commit and tag** the release:
   ```bash
   git commit -m "Release version X.Y.Z"
   git tag -a vX.Y.Z -m "Version X.Y.Z"
   ```

### Changelog Template

Use the template provided in `CHANGELOG.md` for documenting future releases. Each entry should include:
- Version number and date
- Added features
- Changed functionality
- Deprecated features
- Removed features
- Fixed bugs
- Security updates

## Future Development

Areas for future enhancement:
- **Agent Execution**: Currently `af run` parses and validates files; future versions could execute agent workflows via integration with execution platforms
- **Additional Management Commands**: Extend CLI with commands for agent lifecycle management, monitoring, and orchestration
- **Configuration**: Support for global/local config files and environment variables
- **Plugins**: Extensible plugin system for custom commands and parsers
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
