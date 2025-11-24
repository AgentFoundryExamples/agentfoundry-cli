# Agent Foundry CLI Usage Guide

**Version: 1.0.0 (MVP Release)**

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
2. **Parses Content** - Reads and parses the file according to the `.af` format specification
3. **Validates Structure** - Checks that all required keys are present and properly formatted
4. **Outputs JSON** - Emits canonical JSON with deterministic key ordering to stdout
5. **Reports Errors** - Provides detailed error messages with filenames and line numbers to stderr

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
- **Line number** - The specific line where the error occurred (when applicable)
- **Description** - A human-readable explanation of the problem

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

## Workflow Examples

### Basic Validation

Validate a configuration file:
```bash
af run agent.af
```

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

Use in a build script:
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
    if af run "$file" > /dev/null; then
        echo "  ✓ Valid"
    else
        echo "  ✗ Invalid"
    fi
done
```

## Advanced Usage

### Handling Large Files

The `af run` command handles files with large lists efficiently:

```bash
# File with hundreds of must/dont/nice items
af run large-project.af
```

There's no practical limit on list sizes.

### Line Ending Compatibility

The parser handles different line endings:
- Unix (LF)
- Windows (CRLF)
- Classic Mac (CR)

Files with any line ending format will parse correctly.

### UTF-8 Support

The parser:
- Expects UTF-8 encoding
- Handles UTF-8 BOM automatically
- Supports Unicode characters in string values

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
