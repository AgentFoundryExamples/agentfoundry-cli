# Agent Foundry File Format (.af)

**Version: 1.1.0**

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

Lists can be formatted across multiple lines. **When items are on separate lines, commas between items are optional**:

```
# With commas (traditional style)
must: [
    "Complete authentication",
    "Implement data persistence",
    "Add error handling"
]

# Without commas (newline-separated style)
must: [
    "Complete authentication"
    "Implement data persistence"
    "Add error handling"
]
```

Both formats are valid and produce the same result. You can even mix styles:

```
must: [
    "Authentication",       # With comma
    "Data persistence"      # Without comma (newline-separated)
    "Error handling",       # Mixed is fine
]
```

Lists can use single or double quotes for items:

```
dont: ['Skip tests', "Ignore security", 'Forget documentation']
```

Trailing commas are allowed (optional before closing bracket):

```
nice: [
    "Dark mode",
    "Mobile support",
]
```

**Note**: Items on the *same line* must be separated by commas. Commas are only optional when items are on separate lines:

```
# Valid - items on separate lines, no commas needed
must: [
    "Item 1"
    "Item 2"
]

# Invalid - items on same line require commas
must: ["Item 1" "Item 2"]  # This will cause an error!
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

# Required features (using newline-separated style - no commas needed)
must: [
    "User authentication"        # Login system
    "Task creation and editing"  # Core functionality
    "Data persistence"           # Save to database
]

# Things to avoid (using comma-separated style)
dont: [
    "Skip input validation",
    "Ignore security best practices",
    "Forget error handling"
]

# Nice to have features (with trailing comma)
nice: [
    "Dark mode support",
    "Mobile responsive design",
    "Real-time updates",
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

### Legacy vs. New Format Comparison

Both legacy (v1.0) single-line format and new multiline format are fully supported. Existing `.af` files continue to work unchanged.

**Legacy Single-Line Format (v1.0):**
```
purpose: "Build a task management system"
vision: "Create an intuitive tool for tracking tasks"
must: ["User auth", "Task CRUD", "Persistence"]
dont: ["Skip validation", "Ignore security"]
nice: ["Dark mode", "Mobile support"]
```

**New Multiline Format (v1.1):**
```
# More readable with multiline support
purpose: "Build a comprehensive
task management system"

vision: "Create an intuitive tool
for tracking team tasks"

# Newline-separated items (commas optional)
must: [
    "User authentication"     # Inline comment
    "Task CRUD operations"
    "Data persistence"
]

# Traditional comma-separated still works
dont: [
    "Skip validation",
    "Ignore security",
]

nice: ["Dark mode", "Mobile support"]  # Single line OK too
```

Both produce equivalent JSON output. Choose the style that best fits your needs.

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

## UTF-8 Encoding Requirement

Files **must** be encoded in UTF-8. The parser has strict encoding requirements:

**Automatic Handling:**
- UTF-8 BOM (Byte Order Mark) is automatically detected and stripped
- All Unicode characters are supported (emojis, accented characters, CJK scripts, etc.)

**Error Behavior:**
- Files with invalid UTF-8 encoding are rejected with a clear error:
  ```
  Error: File 'config.af': File must be UTF-8 encoded: 'utf-8' codec can't decode byte...
  ```

**Best Practices:**
- Use a text editor that saves files in UTF-8
- Avoid Latin-1, Windows-1252, or other legacy encodings
- Most modern editors default to UTF-8

## Input Size Limits

To prevent resource exhaustion, the parser enforces a strict size limit:

**Maximum Size:** 1 MB (1,048,576 bytes)

**Behavior:**
- Files **at or below** 1 MB: Parsed successfully
- Files **larger than** 1 MB: Rejected before parsing with clear error

**Error Message:**
```
Error: Input file too large: 1500000 bytes (maximum: 1048576 bytes)
```

**Notes:**
- Size is checked before parsing begins
- Same limit applies to stdin input
- The limit is adequate for thousands of configuration items
- If hitting the limit, consider splitting into multiple configuration files

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
- `AFSizeError` - Input exceeds 1MB size limit

All exceptions include filename, line number, and column number information when available.
