# ============================================================
# SPDX-License-Identifier: GPL-3.0-or-later
# This program was generated as part of the AgentFoundry project.
# Copyright (C) 2025  John Brosnihan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ============================================================
"""
Parser and validator for Agent Foundry .af files.

This module provides deterministic parsing and validation utilities for .af files
that normalize keys, enforce schema rules, and emit precise error diagnostics.
"""

import re
from typing import Dict, List, Any, Tuple
from pathlib import Path


class AFParseError(Exception):
    """Base exception for .af file parsing errors."""
    
    def __init__(self, message: str, filename: str = None, line: int = None):
        self.message = message
        self.filename = filename
        self.line = line
        
        # Build full error message with location info
        parts = []
        if filename:
            parts.append(f"File '{filename}'")
        if line is not None:
            parts.append(f"line {line}")
        
        if parts:
            full_message = f"{', '.join(parts)}: {message}"
        else:
            full_message = message
            
        super().__init__(full_message)


class AFMissingKeyError(AFParseError):
    """Exception raised when a required key is missing."""
    pass


class AFDuplicateKeyError(AFParseError):
    """Exception raised when a key appears multiple times."""
    pass


class AFUnknownKeyError(AFParseError):
    """Exception raised when an unknown key is encountered."""
    pass


class AFSyntaxError(AFParseError):
    """Exception raised for syntax errors in .af files."""
    pass


class AFEmptyValueError(AFParseError):
    """Exception raised when a required value is empty."""
    pass


# Required keys in .af files
REQUIRED_KEYS = {'purpose', 'vision', 'must', 'dont', 'nice'}
# Keys that should be strings
STRING_KEYS = {'purpose', 'vision'}
# Keys that should be lists
LIST_KEYS = {'must', 'dont', 'nice'}


def _strip_utf8_bom(content: str) -> str:
    """Remove UTF-8 BOM if present at the beginning of content."""
    if content.startswith('\ufeff'):
        return content[1:]
    return content


def _tokenize_line(line: str, line_num: int, filename: str = None) -> Tuple[str, Any]:
    """
    Tokenize a single line into key and value.
    
    Returns:
        Tuple of (key, value) where value can be str, list, or None for empty lines/comments
    
    Raises:
        AFSyntaxError: If line has invalid syntax
    """
    # Strip whitespace
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None, None
    
    # Check for key-value separator
    if ':' not in line:
        raise AFSyntaxError(
            f"Line missing ':' separator",
            filename=filename,
            line=line_num
        )
    
    # Split on first colon
    key_part, value_part = line.split(':', 1)
    key = key_part.strip().lower()
    value_part = value_part.strip()
    
    # Validate key is not empty
    if not key:
        raise AFSyntaxError(
            "Empty key before ':'",
            filename=filename,
            line=line_num
        )
    
    # Check for unknown keys
    if key not in REQUIRED_KEYS:
        raise AFUnknownKeyError(
            f"Unknown key '{key}' (valid keys: {', '.join(sorted(REQUIRED_KEYS))})",
            filename=filename,
            line=line_num
        )
    
    # Parse value based on key type
    if key in STRING_KEYS:
        # String values - handle quoted strings
        if not value_part:
            raise AFEmptyValueError(
                f"Key '{key}' has empty value",
                filename=filename,
                line=line_num
            )
        
        # Parse quoted string
        value = _parse_quoted_string(value_part, line_num, filename)
        
    elif key in LIST_KEYS:
        # List values - handle list syntax
        if not value_part:
            raise AFEmptyValueError(
                f"Key '{key}' has empty value",
                filename=filename,
                line=line_num
            )
        
        # Parse list
        value = _parse_list(value_part, line_num, filename)
    
    return key, value


def _parse_quoted_string(s: str, line_num: int, filename: str = None) -> str:
    """
    Parse a quoted string, handling both single and double quotes.
    
    Supports:
    - Single quotes: 'text'
    - Double quotes: "text"
    - Apostrophes inside strings: "it's working"
    - Escaped quotes: "say \"hello\""
    
    Raises:
        AFSyntaxError: If string is not properly quoted or has mismatched quotes
    """
    s = s.strip()
    
    # Check if string starts with quote
    if not s or s[0] not in ('"', "'"):
        raise AFSyntaxError(
            f"String value must be quoted (use \" or ')",
            filename=filename,
            line=line_num
        )
    
    quote_char = s[0]
    
    # Find matching closing quote (handle escapes)
    i = 1
    result = []
    while i < len(s):
        char = s[i]
        
        if char == '\\' and i + 1 < len(s):
            # Escape sequence
            next_char = s[i + 1]
            if next_char == quote_char:
                result.append(quote_char)
                i += 2
            elif next_char == '\\':
                result.append('\\')
                i += 2
            elif next_char == 'n':
                result.append('\n')
                i += 2
            elif next_char == 't':
                result.append('\t')
                i += 2
            else:
                # Keep backslash for other cases
                result.append('\\')
                i += 1
        elif char == quote_char:
            # Found closing quote
            # Check for stray characters after closing quote
            remaining = s[i + 1:].strip()
            if remaining:
                raise AFSyntaxError(
                    f"Unexpected characters after closing quote: '{remaining}'",
                    filename=filename,
                    line=line_num
                )
            parsed_result = ''.join(result)
            # Check if result is empty string
            if not parsed_result:
                raise AFEmptyValueError(
                    "String value cannot be empty",
                    filename=filename,
                    line=line_num
                )
            return parsed_result
        else:
            result.append(char)
            i += 1
    
    # Reached end without finding closing quote
    raise AFSyntaxError(
        f"Unterminated string (missing closing {quote_char})",
        filename=filename,
        line=line_num
    )


def _parse_list(s: str, line_num: int, filename: str = None) -> List[str]:
    """
    Parse a list of strings.
    
    Supports:
    - Square bracket notation: ["item1", "item2"]
    - Comma-separated items
    - Quoted strings with apostrophes
    
    Raises:
        AFSyntaxError: If list syntax is invalid
    """
    s = s.strip()
    
    # Check for square brackets
    if not s.startswith('['):
        raise AFSyntaxError(
            "List must start with '['",
            filename=filename,
            line=line_num
        )
    
    if not s.endswith(']'):
        raise AFSyntaxError(
            "List must end with ']'",
            filename=filename,
            line=line_num
        )
    
    # Extract content between brackets
    content = s[1:-1].strip()
    
    # Empty list is not allowed for required keys
    if not content:
        raise AFEmptyValueError(
            "List cannot be empty",
            filename=filename,
            line=line_num
        )
    
    # Parse comma-separated items
    items = []
    current_item = []
    in_quotes = False
    quote_char = None
    escape_next = False
    
    for i, char in enumerate(content):
        if escape_next:
            current_item.append(char)
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            current_item.append(char)
            continue
        
        if char in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = char
            current_item.append(char)
        elif char == quote_char and in_quotes:
            in_quotes = False
            current_item.append(char)
            quote_char = None
        elif char == ',' and not in_quotes:
            # End of item
            item_str = ''.join(current_item).strip()
            if not item_str:
                raise AFSyntaxError(
                    "Empty item in list (consecutive commas or missing value)",
                    filename=filename,
                    line=line_num
                )
            # Parse the quoted string
            parsed = _parse_quoted_string(item_str, line_num, filename)
            items.append(parsed)
            current_item = []
        else:
            current_item.append(char)
    
    # Handle last item
    item_str = ''.join(current_item).strip()
    if item_str:
        # Check for trailing comma (item_str would be empty if valid trailing comma)
        parsed = _parse_quoted_string(item_str, line_num, filename)
        items.append(parsed)
    elif items:  # Only error if there are items (trailing comma after items)
        # This is actually OK - trailing comma after last item
        pass
    
    # Verify we ended quotes properly
    if in_quotes:
        raise AFSyntaxError(
            "Unterminated string in list",
            filename=filename,
            line=line_num
        )
    
    if not items:
        raise AFEmptyValueError(
            "List cannot be empty",
            filename=filename,
            line=line_num
        )
    
    return items


def parse_af_file(filepath: str) -> Dict[str, Any]:
    """
    Parse an Agent Foundry .af file.
    
    Args:
        filepath: Path to the .af file
        
    Returns:
        Dictionary with normalized lowercase keys and typed values:
        - 'purpose': str
        - 'vision': str
        - 'must': List[str]
        - 'dont': List[str]
        - 'nice': List[str]
        
    Raises:
        AFParseError: Base exception for any parsing errors (including wrong extension)
        AFMissingKeyError: When required keys are missing
        AFDuplicateKeyError: When keys appear multiple times
        AFUnknownKeyError: When unknown keys are encountered
        AFSyntaxError: For syntax errors
        AFEmptyValueError: When required values are empty
        FileNotFoundError: If file doesn't exist
    """
    # Validate file exists
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Validate .af suffix (case-insensitive)
    if path.suffix.lower() != '.af':
        raise AFParseError(
            f"File must have .af extension, got: {path.suffix or '(no extension)'}",
            filename=filepath
        )
    
    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise AFParseError(f"File encoding error: {e}", filename=filepath)
    
    # Strip UTF-8 BOM if present
    content = _strip_utf8_bom(content)
    
    # Parse line by line
    result = {}
    seen_keys = {}  # Track where each key was first seen
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, start=1):
        try:
            key, value = _tokenize_line(line, line_num, filepath)
            
            # Skip empty lines and comments
            if key is None:
                continue
            
            # Check for duplicate keys (case-insensitive)
            if key in result:
                raise AFDuplicateKeyError(
                    f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                    filename=filepath,
                    line=line_num
                )
            
            # Store key and value
            result[key] = value
            seen_keys[key] = line_num
            
        except AFParseError:
            # Re-raise our exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise AFParseError(
                f"Unexpected error: {e}",
                filename=filepath,
                line=line_num
            )
    
    # Verify all required keys are present
    missing_keys = REQUIRED_KEYS - set(result.keys())
    if missing_keys:
        raise AFMissingKeyError(
            f"Missing required keys: {', '.join(sorted(missing_keys))}",
            filename=filepath
        )
    
    return result


def validate_af_content(content: str, filename: str = None) -> Dict[str, Any]:
    """
    Parse and validate .af content from a string.
    
    Useful for testing without file I/O.
    
    Args:
        content: String content of .af file
        filename: Optional filename for error messages
        
    Returns:
        Dictionary with normalized lowercase keys and typed values
        
    Raises:
        AFParseError and subclasses for validation errors
    """
    # Strip UTF-8 BOM if present
    content = _strip_utf8_bom(content)
    
    # Parse line by line
    result = {}
    seen_keys = {}
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, start=1):
        key, value = _tokenize_line(line, line_num, filename)
        
        # Skip empty lines and comments
        if key is None:
            continue
        
        # Check for duplicate keys
        if key in result:
            raise AFDuplicateKeyError(
                f"Duplicate key '{key}' (first seen on line {seen_keys[key]})",
                filename=filename,
                line=line_num
            )
        
        result[key] = value
        seen_keys[key] = line_num
    
    # Verify all required keys are present
    missing_keys = REQUIRED_KEYS - set(result.keys())
    if missing_keys:
        raise AFMissingKeyError(
            f"Missing required keys: {', '.join(sorted(missing_keys))}",
            filename=filename
        )
    
    return result
