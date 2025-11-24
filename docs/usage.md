# Agent Foundry CLI Usage Guide

**Version: 1.1.0**

This guide provides detailed information on using the Agent Foundry CLI (`af`) command-line tool.

## Table of Contents

- [Installation](#installation)
- [Basic Commands](#basic-commands)
- [Running Agent Foundry Files](#running-agent-foundry-files)
- [Understanding Output](#understanding-output)
- [Error Handling](#error-handling)
- [Workflow Examples](#workflow-examples)
- [Advanced Usage](#advanced-usage)

## Installation

Install the Agent Foundry CLI in a virtual environment:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install CLI
pip install -e .
```

## Basic Commands

### Getting Help

```bash
# Display main help
af --help

# Display help for a specific command
af run --help
```

### Version Information

```bash
af version
```

Output:
```
Agent Foundry CLI version: 1.0.0
```

## Running Agent Foundry Files

The `af run` command is the primary tool for parsing and validating Agent Foundry configuration files.

### Basic Usage

```bash
af run path/to/file.af
```

### What It Does

The `af run` command:

1. **Validates Extension** - Ensures the file has a `.af` extension (case-insensitive)
2. **Checks Size** - Rejects files larger than 1 MB before parsing
3. **Validates Encoding** - Ensures UTF-8 encoding, strips BOM if present
4. **Parses Content** - Tokenizes and parses using state machine
5. **Validates Structure** - Checks that all required keys are present and properly formatted
6. **Outputs JSON** - Emits canonical JSON with deterministic key ordering to stdout
7. **Reports Errors** - Provides detailed error messages with filenames, line numbers, and column positions to stderr

### Example

```bash
af run examples/example.af
```

Output:
```json
{
  "purpose": "Build a comprehensive task management system",
  "vision": "Create an intuitive and powerful tool for tracking team tasks and projects",
  "must": [
    "User authentication and authorization",
    "Task creation, editing, and deletion",
    "Data persistence with database",
    "Input validation and error handling"
  ],
  "dont": [
    "Skip security best practices",
    "Ignore input validation",
    "Forget error handling",
    "Deploy without testing"
  ],
  "nice": [
    "Dark mode support",
    "Mobile responsive design",
    "Real-time collaboration",
    "Email notifications",
    "Advanced search and filtering"
  ]
}
```

## Understanding Output

### Success Case

When successful, `af run`:
- Exits with code `0`
- Outputs **only** JSON to stdout (no extra text or logging)
- Outputs nothing to stderr

### Canonical JSON Ordering

The JSON output always has keys in this order:
1. `purpose`
2. `vision`
3. `must`
4. `dont`
5. `nice`

This deterministic ordering ensures consistency across runs and makes it suitable for:
- Version control (predictable diffs)
- Automated testing
- Piping to other tools

## Error Handling

### Exit Codes

- `0` - Success: file parsed successfully
- `1` - Error: validation or parsing failure
- `2` - Usage error: missing required arguments

### Error Messages

Errors are written to stderr and include:
- **Filename** - The path to the file being processed
- **Line number** - The specific line where the error occurred
- **Column number** - The exact column position of the error
- **Caret indicator** - A visual marker (^) pointing to the exact error location
- **Fuzzy suggestions** - For typos in key names, suggests the closest valid key

#### Typo in Key Name
```bash
$ af run config.af
Error: File 'config.af', line 2, column 1: Unknown key 'pourpose' (did you mean 'purpose'?)
pourpose: "Build a task manager"
^
```

### Common Errors

#### File Not Found
```bash
$ af run nonexistent.af
Error: File not found: nonexistent.af
```

#### Wrong Extension
```bash
$ af run config.txt
Error: File 'config.txt': File must have .af extension, got: .txt
```

#### Missing Required Key
```bash
$ af run incomplete.af
Error: File 'incomplete.af': Missing required keys: nice
```

#### Syntax Error
```bash
$ af run malformed.af
Error: File 'malformed.af', line 2: String value must be quoted (use " or ')
```

#### Duplicate Key
```bash
$ af run duplicate.af
Error: File 'duplicate.af', line 5: Duplicate key 'purpose' (first seen on line 2)
```

#### File Too Large
```bash
$ af run huge.af
Error: File 'huge.af': Input file too large: 1048580 bytes (maximum: 1048576 bytes)
```

#### Invalid UTF-8 Encoding
```bash
$ af run bad-encoding.af
Error: File 'bad-encoding.af': File must be UTF-8 encoded: ...
```

#### Empty File
```bash
$ af run empty.af
Error: File 'empty.af', line 1: Missing required keys: dont, must, nice, purpose, vision
```

## Workflow Examples

### Basic Validation

Validate a configuration file:
```bash
af run agent.af
```

### Silent Validation with `af validate`

For CI/CD pipelines where you only need the exit code, use `af validate`:

```bash
# Validate silently - no output on success
af validate agent.af

# Use in shell conditionals
if af validate agent.af; then
    echo "Configuration is valid"
    deploy_application
else
    echo "Configuration is invalid"
    exit 1
fi

# Validate from stdin
cat config.af | af validate -
```

**Exit Codes:**
- `0` - Valid: the file parsed successfully
- `1` - Invalid: validation or parsing failure
- `2` - Usage error: missing required arguments

**Differences from `af run`:**
- Suppresses stdout on success (silent mode)
- Only writes to stderr on errors
- Ideal for CI/CD where you only check exit codes

### Extract Specific Fields with jq

```bash
# Get the purpose
af run agent.af | jq -r '.purpose'

# Get the first must-do item
af run agent.af | jq -r '.must[0]'

# Count nice-to-have items
af run agent.af | jq '.nice | length'

# Get all dont items as a comma-separated list
af run agent.af | jq -r '.dont | join(", ")'
```

### Validation in CI/CD

Use `af validate` in build scripts for clean CI logs:
```bash
#!/bin/bash
set -e

echo "Validating agent configuration..."
af validate config/agent.af

echo "Configuration valid!"
```

Or with `af run` if you need the output:
```bash
#!/bin/bash
set -e

echo "Validating agent configuration..."
af run config/agent.af > /dev/null

echo "Configuration valid!"
```

### Comparing Configurations

Compare two configurations:
```bash
# Save outputs
af run old.af > old.json
af run new.af > new.json

# Use diff or other tools
diff old.json new.json
```

### Batch Processing

Validate multiple files:
```bash
for file in configs/*.af; do
    echo "Validating $file..."
    if af validate "$file"; then
        echo "  ✓ Valid"
    else
        echo "  ✗ Invalid"
    fi
done
```

## Advanced Usage

### Reading from stdin

Use `-` as the file argument to read from stdin, enabling pipeline workflows:

```bash
# Pipe content directly
echo 'purpose: "Test"
vision: "Test"
must: ["Item"]
dont: ["Item"]
nice: ["Item"]' | af run -

# Pipe a file through stdin
cat config.af | af run -

# Use with heredoc
af run - <<EOF
purpose: "Dynamic config"
vision: "Generated at runtime"
must: ["Feature 1"]
dont: ["Skip tests"]
nice: ["Polish UI"]
EOF
```

**stdin Guarantees:**
- Same 1 MB size limit as files
- Same UTF-8 encoding requirement
- Same BOM stripping behavior
- Same validation and error reporting

**Programmatic Usage:**
```python
from agentfoundry_cli.parser import parse_af_stdin

result = parse_af_stdin()
```

### Handling Large Files

The `af run` command processes files efficiently up to the 1 MB limit:

```bash
# File with hundreds of must/dont/nice items (but under 1 MB)
af run large-project.af
```

**Limits:**
- Maximum file size: 1 MB (1,048,576 bytes)
- No practical limit on number of list items (within the size limit)
- Parsing is fast (typically < 100ms)

### Line Ending Compatibility

The parser handles different line endings:
- Unix (LF)
- Windows (CRLF)
- Classic Mac (CR)

Files with any line ending format will parse correctly.

### UTF-8 Support and Requirements

The parser has strict UTF-8 requirements with robust support:

**Required:**
- All `.af` files **must** be UTF-8 encoded
- Files with other encodings (e.g., Latin-1, Windows-1252) will be rejected with a clear error

**Automatic Handling:**
- UTF-8 BOM (Byte Order Mark) is automatically detected and stripped
- Works correctly even if BOM appears at the start of the file

**Full Unicode Support:**
- Emojis: `"Deploy the app 🚀"`
- Accented characters: `"Café système with naïve approach"`
- Asian scripts: `"Support 日本語 中文 한글"`
- Mathematical symbols: `"Test α β γ"`
- Arabic/RTL: `"مرحبا العالم"`

**Example:**
```af
purpose: "Build an app 🚀 with café ☕"
vision: "Support 日本語 and other languages"
must: ["Handle UTF-8 properly", "Support emojis 😊"]
dont: ["Assume ASCII only"]
nice: ["Add ñ ü ö support"]
```

### Input Size Limits

To prevent resource exhaustion, the parser enforces strict size limits:

**Size Limit:** 1 MB (1,048,576 bytes)

**Behavior:**
- Files **at or below** 1 MB: Parsed successfully
- Files **larger than** 1 MB: Rejected with clear error before parsing
- Applies to both file input and stdin

**Error Message:**
```
Error: Input file too large: 1048580 bytes (maximum: 1048576 bytes)
```

**Best Practices:**
- Keep `.af` files focused and concise
- Use external documentation for extensive details
- If hitting the limit, consider splitting into multiple configuration files

**Why 1 MB?**
- Prevents accidental processing of huge files
- Ensures fast parsing (< 100ms for typical files)
- Adequate for thousands of configuration items

### Piping and Redirection

#### Pipe to Other Tools
```bash
# Parse and format
af run agent.af | jq .

# Extract and process
af run agent.af | jq -r '.must[]' | while read item; do
    echo "TODO: $item"
done
```

#### Redirect Output
```bash
# Save JSON to file
af run agent.af > config.json

# Separate stdout and stderr
af run agent.af > output.json 2> errors.txt
```

#### Check Status
```bash
# Use exit code in scripts
if af run agent.af > /dev/null 2>&1; then
    echo "Valid configuration"
else
    echo "Invalid configuration"
    exit 1
fi
```

### Literal Filename Handling

The `run` command treats arguments as literal filenames, even if they match command names:

```bash
# This parses a file named "help.af", not a help command
af run help.af

# This parses a file named "version.af"
af run version.af
```

## Sample Files

### Minimal Example

`minimal.af`:
```
purpose: "Simple task tracker"
vision: "Easy task management"
must: ["Create tasks"]
dont: ["Overcomplicate"]
nice: ["Dark mode"]
```

### Comprehensive Example

See [examples/example.af](../examples/example.af) for a full-featured example demonstrating:
- Descriptive purpose and vision
- Multiple must-have requirements
- Important constraints in dont
- Optional nice-to-have features
- Proper formatting and comments

### Multiline Example

`multiline.af`:
```
# Configuration with multiline strings and lists
purpose: "Build a comprehensive
task management system
that teams will love"

vision: "Create an intuitive tool
that empowers collaboration"

# Core features (using newline-separated style - commas optional)
must: [
    "User authentication"        # Login system
    "Task creation and editing"  # CRUD operations
    "Data persistence"           # Database
]

# Avoid these (using comma-separated style)
dont: [
    "Skip input validation",
    "Ignore security"
]

# Future enhancements (trailing comma OK)
nice: [
    "Dark mode support",
    "Mobile responsive design",
]
```
- Optional nice-to-have features
- Proper formatting and comments

## Next Steps

- Read the [format specification](format.md) for `.af` file syntax
- See [development guide](development.md) for contributing
- Check the [README](../README.md) for installation options

## Troubleshooting

### Command Not Found

If `af` command is not found:
```bash
# Ensure you're in the virtual environment
which af

# Reinstall if needed
pip install -e .
```

### Import Errors

If you get import errors:
```bash
# Ensure dependencies are installed
pip install -e ".[dev]"
```

### Permission Errors

If you can't read the `.af` file:
```bash
# Check file permissions
ls -l file.af

# Fix if needed
chmod +r file.af
```
