# Agent Foundry File Format (.af)

**Version: 1.0.0 (MVP Release)**

This document describes the syntax and structure of Agent Foundry `.af` files used to define agent configurations.

## Overview

Agent Foundry files (`.af`) use a simple, human-readable format to define agent purpose, vision, and behavioral constraints. The format consists of key-value pairs where keys are case-insensitive and values are either quoted strings or lists of quoted strings.

**Important**: Files must have the `.af` extension (case-insensitive). The parser will reject files without this extension to prevent accidentally processing incorrectly named or unintended files.

## File Structure

An `.af` file must contain exactly five required keys:

- `purpose` - A string describing what the agent should accomplish
- `vision` - A string describing the desired outcome or end state
- `must` - A list of strings specifying required behaviors or constraints
- `dont` - A list of strings specifying behaviors to avoid
- `nice` - A list of strings specifying optional enhancements

## Syntax

### Basic Format

```
key: value
```

Keys are case-insensitive (e.g., `PURPOSE`, `purpose`, and `Purpose` are equivalent).

### Comments

Lines starting with `#` are treated as comments and ignored. Comments can also appear after meaningful tokens on the same line (inline comments):

```
# This is a standalone comment
purpose: "Build a task manager" # This is an inline comment
```

### String Values

String values for `purpose` and `vision` must be enclosed in quotes (single or double). **Strings can now span multiple lines**, with embedded newlines preserved in the JSON output:

```
purpose: "Build a comprehensive task management system"
vision: 'Create an intuitive tool for tracking tasks'
```

#### Multiline Strings

You can split long strings across multiple lines. The actual newline characters will be preserved in the output:

```
purpose: "Build a comprehensive
task management system
that is easy to use"
```

This preserves the newlines in the JSON output.

#### Quotes and Apostrophes

Strings can contain apostrophes:

```
purpose: "It's a task management system"
```

Escaped quotes are supported:

```
purpose: "Say \"hello\" to the user"
```

#### Escape Sequences

The following escape sequences are supported in strings:

- `\"` - Double quote
- `\'` - Single quote (apostrophe)
- `\\` - Backslash
- `\n` - Newline
- `\t` - Tab

### List Values

Lists for `must`, `dont`, and `nice` use square bracket notation with comma-separated quoted strings. **Lists can now span multiple lines** for better readability:

```
must: ["Complete authentication", "Implement data persistence", "Add error handling"]
```

#### Multiline Lists

Lists can be formatted across multiple lines with items on separate lines:

```
must: [
    "Complete authentication",
    "Implement data persistence",
    "Add error handling"
]
```

Lists can use single or double quotes for items:

```
dont: ['Skip tests', "Ignore security", 'Forget documentation']
```

Trailing commas are allowed:

```
nice: [
    "Dark mode",
    "Mobile support",
]
```

Comments can appear within multiline lists:

```
must: [
    "Authentication",  # User login
    "Data persistence", # Database
    "Error handling"   # Proper errors
]
```

### Whitespace

The parser is tolerant of whitespace:

```
  purpose  :   "Build a task manager"
must   :["Item 1",  "Item 2"]
```

## Complete Example

```
# Task Management System Configuration

purpose: "Build a comprehensive task management system"
vision: "Create an intuitive and powerful tool for tracking team tasks"

# Required features
must: [
    "User authentication",       # Login system
    "Task creation and editing", # Core functionality
    "Data persistence"           # Save to database
]

# Things to avoid
dont: [
    "Skip input validation",
    "Ignore security best practices",
    "Forget error handling"
]

# Nice to have features
nice: [
    "Dark mode support",
    "Mobile responsive design",
    "Real-time updates"
]
```

### Multiline String Example

```
purpose: "Build a comprehensive
task management system
with team collaboration"

vision: "Create an intuitive tool
that empowers teams
to work more efficiently"

must: [
    "User authentication",
    "Task management"
]
dont: ["Skip tests"]
nice: ["Dark mode"]
```

## Error Reporting

The parser provides detailed error messages including:

- **Filename** - The path to the `.af` file
- **Line number** - The specific line where the error occurred
- **Column number** - The exact column position of the error
- **Caret indicator** - A visual pointer (^) showing exactly where the error is
- **Fuzzy matching** - Suggestions for typos in key names (e.g., "Did you mean 'purpose'?")

### Common Errors

#### Unknown Keys with Suggestions

The parser uses fuzzy matching to suggest corrections for typos:

```
Error: File 'example.af', line 3, column 1: Unknown key 'pourpose' (did you mean 'purpose'?)
pourpose: "Build a task manager"
^
```

When the typo is too different, no suggestion is provided:

```
Error: File 'example.af', line 7, column 1: Unknown key 'completely_wrong'
completely_wrong: "This should fail"
^
```

#### Missing Required Keys

```
Error: File 'example.af': Missing required keys: purpose
```

All five required keys (`purpose`, `vision`, `must`, `dont`, `nice`) must be present.

#### Duplicate Keys

```
Error: File 'example.af', line 5: Duplicate key 'purpose' (first seen on line 2)
```

Each key can only appear once (case-insensitive).

#### Unknown Keys

```
Error: File 'example.af', line 7: Unknown key 'extra' (did you mean 'nice'?)
```

Only the five required keys are allowed. The parser will suggest similar keys if you make a typo.

#### Syntax Errors

Unquoted strings:
```
Error: File 'example.af', line 2: String value must be quoted (use " or ')
```

Unterminated strings:
```
Error: File 'example.af', line 3: Unterminated string (missing closing ")
```

Missing list brackets:
```
Error: File 'example.af', line 4: List must start with '['
```

Empty values:
```
Error: File 'example.af', line 5: Key 'purpose' has empty value
```

Stray characters:
```
Error: File 'example.af', line 6: Unexpected characters after closing quote: 'extra'
```

## Best Practices

1. **Use meaningful descriptions** - Make purpose and vision clear and specific
2. **Be explicit in constraints** - List concrete must/dont items rather than vague guidelines
3. **Keep lists focused** - Each list item should be a single, actionable constraint
4. **Use consistent quoting** - Choose either single or double quotes and stick with it
5. **Add comments** - Use comments to organize sections and explain intent
6. **Handle apostrophes properly** - Use double quotes for strings containing apostrophes

## UTF-8 Support

Files should be encoded in UTF-8. The parser automatically handles UTF-8 BOM (Byte Order Mark) if present.

## Limitations

- **No nested structures** - Lists cannot contain sublists or nested objects
- **Fixed schema** - Only the five required keys are supported
- **No variable interpolation** - Values are literal strings, no variable substitution

## Usage in Code

### Python API

```python
from agentfoundry_cli.parser import parse_af_file, AFParseError

try:
    config = parse_af_file("agent.af")
    print(f"Purpose: {config['purpose']}")
    print(f"Must do: {config['must']}")
except AFParseError as e:
    print(f"Error parsing file: {e}")
```

### Return Value

The parser returns a dictionary with normalized lowercase keys:

```python
{
    'purpose': str,      # Single string value
    'vision': str,       # Single string value
    'must': List[str],   # List of strings
    'dont': List[str],   # List of strings
    'nice': List[str]    # List of strings
}
```

## Exception Types

The parser raises typed exceptions for different error scenarios:

- `AFParseError` - Base exception for all parsing errors
- `AFMissingKeyError` - Required key is missing
- `AFDuplicateKeyError` - Key appears multiple times
- `AFUnknownKeyError` - Unknown key encountered
- `AFSyntaxError` - Syntax error in file structure
- `AFEmptyValueError` - Required value is empty

All exceptions include filename and line number information when available.
