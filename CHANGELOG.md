# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-24

### Overview

This release introduces a refactored tokenizer-driven parser architecture, enhanced CLI capabilities with stdin support and a new `af validate` command, and improved error reporting with precise column positions and visual caret indicators.

### Added

#### CLI Enhancements
- **`af validate` command** - Silent validation for CI/CD pipelines
  - Suppresses stdout on success (exit code 0)
  - Errors written to stderr (exit code 1)
  - Same validation as `af run` without JSON output
  - Usage: `af validate config.af` or `af validate -`
- **stdin support** - Read `.af` content from stdin using `-`
  - `af run -` - Parse stdin and output JSON
  - `af validate -` - Validate stdin silently
  - Same 1MB size limit and UTF-8 requirement as file input
  - Enables pipeline workflows: `cat config.af | af run -`

#### Parser Refactor
- **Tokenizer-driven state machine** - Complete rewrite of parser architecture
  - Character-by-character scanning with precise position tracking
  - Token types: KEY, COLON, STRING, LBRACKET, RBRACKET, COMMA, COMMENT, NEWLINE, EOF
  - Line and column numbers for every token
  - Lookahead support for escape sequence handling
- **Multiline strings** - String values can now span multiple lines
  - Embedded newlines preserved in JSON output
  - Works for `purpose` and `vision` keys
- **Multiline lists** - Lists can be formatted across multiple lines
  - Newline-separated items (commas optional between lines)
  - Comments allowed within multiline lists
  - Mixed comma/newline separation supported
- **Trailing commas** - Optional trailing comma before closing `]`
- **Inline comments** - Comments after values on the same line
  - `purpose: "Build app" # This is an inline comment`
  - Comments within multiline lists

#### Error Reporting Improvements
- **Column numbers** - All errors now include precise column positions
- **Caret indicators** - Visual `^` pointer showing exact error location
- **Fuzzy key suggestions** - Typo detection with "did you mean?" suggestions
  - Uses Levenshtein distance (max 2 edits)
  - Example: `pourpose` suggests `purpose`
- **Source line display** - Shows the offending line in error output

#### Input Validation
- **1MB size limit** - Files and stdin rejected if larger than 1,048,576 bytes
  - Clear error: `Input file too large: X bytes (maximum: 1048576 bytes)`
  - Checked before parsing to prevent resource exhaustion
- **UTF-8 requirement** - Strict UTF-8 encoding enforcement
  - Clear error for invalid encoding
  - BOM automatically stripped if present

### Changed

- Parser now uses tokenizer-driven architecture instead of line-by-line parsing
- Error messages now include column numbers in addition to line numbers
- Test suite expanded from 76 to 142 tests

### Technical Details

- **Backward compatibility**: Full v1.0 syntax compatibility maintained
  - Single-line key-value pairs still work
  - Comma-separated lists still work
  - All existing `.af` files parse correctly
- **Canonical key order**: Output always uses `purpose, vision, must, dont, nice` order
- **Exit codes**: 0 (success), 1 (validation error), 2 (usage error)

---

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

- [1.1.0] - 2025-11-24 - Parser refactor, CLI enhancements, enhanced error reporting
- [1.0.0] - 2025-11-24 - Initial MVP release

[1.1.0]: https://github.com/AgentFoundryExamples/agentfoundry-cli/releases/tag/v1.1.0
[1.0.0]: https://github.com/AgentFoundryExamples/agentfoundry-cli/releases/tag/v1.0.0
