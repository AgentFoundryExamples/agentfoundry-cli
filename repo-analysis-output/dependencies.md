# Dependency Graph

Intra-repository dependency analysis for Python and JavaScript/TypeScript files.

Includes classification of external dependencies as stdlib vs third-party.

## Statistics

- **Total files**: 8
- **Intra-repo dependencies**: 7
- **External stdlib dependencies**: 16
- **External third-party dependencies**: 3

## External Dependencies

### Standard Library / Core Modules

Total: 16 unique modules

- `dataclasses.dataclass`
- `enum.Enum`
- `enum.auto`
- `io`
- `json`
- `os`
- `pathlib.Path`
- `re`
- `sys`
- `tempfile`
- `typing.Any`
- `typing.Dict`
- `typing.List`
- `typing.Optional`
- `typing.TextIO`
- `typing.Tuple`

### Third-Party Packages

Total: 3 unique packages

- `pytest`
- `typer`
- `typer.testing.CliRunner`

## Most Depended Upon Files (Intra-Repo)

- `agentfoundry_cli/cli.py` (3 dependents)
- `agentfoundry_cli/__init__.py` (2 dependents)
- `agentfoundry_cli/parser.py` (2 dependents)

## Files with Most Dependencies (Intra-Repo)

- `agentfoundry_cli/cli.py` (2 dependencies)
- `tests/test_cli.py` (2 dependencies)
- `agentfoundry_cli/__main__.py` (1 dependencies)
- `tests/test_cli_run.py` (1 dependencies)
- `tests/test_parser.py` (1 dependencies)
