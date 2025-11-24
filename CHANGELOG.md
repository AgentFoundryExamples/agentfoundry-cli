# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-24

### Overview

Initial MVP release of Agent Foundry CLI providing a complete command-line interface for parsing and validating Agent Foundry configuration files.

### Added

#### Core CLI Features
- **Typer-based CLI framework** - Built with [Typer](https://typer.tiangolo.com/) for intuitive command-line interface with rich terminal output
- **`af run` command** - Parse and validate `.af` (Agent Foundry) configuration files
  - Validates file extension (must be `.af`, case-insensitive)
  - Parses file syntax according to Agent Foundry format specification
  - Validates structure ensuring all required keys are present
  - Outputs canonical JSON with deterministic key ordering to stdout
  - Provides detailed error messages with filename and line numbers to stderr
- **`af version` command** - Display CLI version information
- **`af help` command** - Display comprehensive help for CLI and specific commands
- **`af hello` command** - Simple placeholder command demonstrating CLI structure

#### Parser and Validator
- **Robust `.af` file parser** - Comprehensive parser with detailed error reporting
  - Supports case-insensitive keys: `purpose`, `vision`, `must`, `dont`, `nice`
  - Supports quoted strings (single and double quotes)
  - Supports escape sequences: `\"`, `\'`, `\\`, `\n`, `\t`
  - Supports list values with comma-separated quoted strings
  - Handles apostrophes and special characters in strings
  - Tolerant of whitespace variations
  - Handles different line endings (Unix LF, Windows CRLF, Classic Mac CR)
  - UTF-8 encoding support with automatic BOM handling
  - Comments support (lines starting with `#`)
  
#### Error Handling
- **Comprehensive error messages** including:
  - File not found errors
  - Invalid file extension errors
  - Missing required keys
  - Duplicate key detection
  - Unknown key detection
  - Syntax errors with line numbers
  - Empty value detection
  - Unterminated string detection
  - List formatting errors

#### Testing
- **Comprehensive test suite** with 76 tests covering:
  - CLI command functionality
  - Parser validation logic
  - Error handling scenarios
  - Edge cases (large files, different encodings, line endings)
  - Integration tests for end-to-end workflows
- **pytest configuration** with coverage reporting
- **Test coverage** for all core features and error paths

#### Documentation
- **README.md** - User-facing documentation with installation and usage instructions
- **docs/usage.md** - Detailed usage guide with examples and workflows
- **docs/format.md** - Complete `.af` file format specification
- **docs/development.md** - Development and contribution guidelines
- **example.af** - Reference example demonstrating proper `.af` file format

#### Example Files
- **example.af** - Comprehensive example demonstrating:
  - Task management system configuration
  - All required keys with meaningful values
  - Proper formatting and comments
  - List structures with multiple items

### Technical Details

- **Python version support**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Exit codes**: 0 (success), 1 (parsing/validation error), 2 (usage error)
- **Output format**: Canonical JSON with ordered keys (purpose, vision, must, dont, nice)
- **License**: GPLv3 or later

### Dependencies

- typer[all] >= 0.9.0 (includes rich for terminal output)
- pytest >= 7.0.0 (dev)
- pytest-cov >= 4.0.0 (dev)

---

## Future Releases Template

Use the following template for documenting future releases:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security updates
```

## Version History

- [1.0.0] - 2025-11-24 - Initial MVP release

[1.0.0]: https://github.com/AgentFoundryExamples/agentfoundry-cli/releases/tag/v1.0.0
