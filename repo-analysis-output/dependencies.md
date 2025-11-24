# Dependency Graph

Intra-repository dependency analysis for Python and JavaScript/TypeScript files.

Includes classification of external dependencies as stdlib vs third-party.

## Statistics

- **Total files**: 7
- **Intra-repo dependencies**: 5
- **External stdlib dependencies**: 9
- **External third-party dependencies**: 3

## External Dependencies

### Standard Library / Core Modules

Total: 9 unique modules

- `os`
- `pathlib.Path`
- `re`
- `tempfile`
- `typing.Any`
- `typing.Dict`
- `typing.List`
- `typing.Optional`
- `typing.Tuple`

### Third-Party Packages

Total: 3 unique packages

- `pytest`
- `typer`
- `typer.testing.CliRunner`

## Most Depended Upon Files (Intra-Repo)

- `agentfoundry_cli/cli.py` (2 dependents)
- `agentfoundry_cli/__init__.py` (2 dependents)
- `agentfoundry_cli/parser.py` (1 dependents)

## Files with Most Dependencies (Intra-Repo)

- `tests/test_cli.py` (2 dependencies)
- `agentfoundry_cli/__main__.py` (1 dependencies)
- `agentfoundry_cli/cli.py` (1 dependencies)
- `tests/test_parser.py` (1 dependencies)
