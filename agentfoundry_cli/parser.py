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

Architecture:
    The parser uses a tokenizer-driven approach for robust handling of UTF-8 input,
    size validation, and backwards-compatible v1.0 syntax:
    
    1. Tokenizer: Scans input character-by-character, emitting tokens (KEY, STRING,
       LBRACKET, RBRACKET, COMMA, COMMENT, NEWLINE, EOF) with position tracking.
    
    2. State Machine: Consumes tokens to build the flat purpose/vision/must/dont/nice
       structure while maintaining canonical order and v1.0 compatibility.
    
    3. Input Loading: Enforces UTF-8 decoding, normalizes BOM, and rejects payloads
       larger than 1MB with clear error messages.

Guarantees:
    - UTF-8 encoding required; BOM stripped automatically
    - Maximum input size: 1MB (1,048,576 bytes)
    - Deterministic token/position tracking for error reporting
    - No eval/exec; fixed JSON output shape
"""

import sys
import io
from enum import Enum, auto
from typing import Dict, List, Any, Tuple, Optional, TextIO
from pathlib import Path
from dataclasses import dataclass


def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate the Levenshtein distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance between s1 and s2
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def _find_closest_key(unknown_key: str, valid_keys: set) -> Optional[str]:
    """
    Find the closest matching valid key using Levenshtein distance.
    
    Args:
        unknown_key: The unknown key entered by the user
        valid_keys: Set of valid keys
        
    Returns:
        The closest matching key if distance <= 2, otherwise None
    """
    min_distance = float('inf')
    closest_key = None
    
    for valid_key in valid_keys:
        distance = _levenshtein_distance(unknown_key.lower(), valid_key.lower())
        if distance < min_distance:
            min_distance = distance
            closest_key = valid_key
    
    # Only suggest if distance is <= 2 (reasonable typo distance)
    if min_distance <= 2:
        return closest_key
    
    return None


# Maximum input size: 1MB
MAX_INPUT_SIZE = 1024 * 1024  # 1,048,576 bytes


class TokenType(Enum):
    """Token types for the tokenizer."""
    KEY = auto()           # Identifier before colon
    COLON = auto()         # :
    STRING = auto()        # Quoted string value
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    COMMA = auto()         # ,
    COMMENT = auto()       # # to end of line
    NEWLINE = auto()       # \n or \r\n
    EOF = auto()           # End of file
    WHITESPACE = auto()    # Spaces, tabs (not newlines)


@dataclass
class Token:
    """Represents a single token with position information."""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class AFParseError(Exception):
    """Base exception for .af file parsing errors."""
    
    def __init__(self, message: str, filename: str = None, line: int = None, column: int = None, 
                 source_line: str = None):
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        self.source_line = source_line
        
        # Build full error message with location info
        parts = []
        if filename:
            parts.append(f"File '{filename}'")
        if line is not None:
            if column is not None:
                parts.append(f"line {line}, column {column}")
            else:
                parts.append(f"line {line}")
        
        if parts:
            full_message = f"{', '.join(parts)}: {message}"
        else:
            full_message = message
        
        # Add caret indicator if we have line and column info
        if source_line and line is not None and column is not None:
            full_message += f"\n{source_line}"
            # Add caret pointing to the error column
            full_message += f"\n{' ' * (column - 1)}^"
            
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


class AFSizeError(AFParseError):
    """Exception raised when input exceeds size limits."""
    pass


# Required keys in .af files
REQUIRED_KEYS = {'purpose', 'vision', 'must', 'dont', 'nice'}
# Canonical key order for output
CANONICAL_KEY_ORDER = ['purpose', 'vision', 'must', 'dont', 'nice']
# Keys that should be strings
STRING_KEYS = {'purpose', 'vision'}
# Keys that should be lists
LIST_KEYS = {'must', 'dont', 'nice'}


def _strip_utf8_bom(content: str) -> str:
    """Remove UTF-8 BOM if present at the beginning of content."""
    if content.startswith('\ufeff'):
        return content[1:]
    return content


def load_input(source: Optional[str] = None, stream: Optional[TextIO] = None) -> str:
    """
    Load and validate input from file or stream with size and encoding checks.
    
    Args:
        source: Path to file to read (mutually exclusive with stream)
        stream: Text stream to read from (mutually exclusive with source)
        
    Returns:
        UTF-8 decoded content with BOM stripped
        
    Raises:
        AFSizeError: If input exceeds 1MB limit
        AFParseError: If encoding is invalid
        ValueError: If neither or both source and stream are provided
    """
    if (source is None) == (stream is None):
        raise ValueError("Exactly one of source or stream must be provided")
    
    if source:
        # Read from file
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        
        # Check file size before reading
        file_size = path.stat().st_size
        if file_size > MAX_INPUT_SIZE:
            raise AFSizeError(
                f"Input file too large: {file_size} bytes (maximum: {MAX_INPUT_SIZE} bytes)",
                filename=source
            )
        
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise AFParseError(
                f"File must be UTF-8 encoded: {e}",
                filename=source
            )
    else:
        # Read from stream
        try:
            # Read with size limit - try to read one byte more than the limit
            # to detect if stream exceeds the limit
            content = stream.read(MAX_INPUT_SIZE + 1)
            if len(content) > MAX_INPUT_SIZE:
                raise AFSizeError(
                    f"Input too large: exceeds {MAX_INPUT_SIZE} bytes (1MB) limit"
                )
        except UnicodeDecodeError as e:
            raise AFParseError(f"Input must be UTF-8 encoded: {e}")
    
    # Verify we didn't exceed size limit after reading
    # (encoding can expand byte size)
    if len(content.encode('utf-8')) > MAX_INPUT_SIZE:
        raise AFSizeError(
            f"Input too large: exceeds {MAX_INPUT_SIZE} bytes (1MB) limit",
            filename=source
        )
    
    # Strip BOM if present
    return _strip_utf8_bom(content)


class Tokenizer:
    """
    Tokenizer for .af files using character-by-character scanning.
    
    Emits tokens with precise line and column position tracking for
    error reporting.
    """
    
    def __init__(self, content: str, filename: str = None):
        self.content = content
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        # Store lines for error reporting with caret indicators
        self.lines = content.splitlines(keepends=False)
        
    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character at current position + offset without consuming."""
        pos = self.pos + offset
        if pos < len(self.content):
            return self.content[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Consume and return current character, updating position."""
        if self.pos >= len(self.content):
            return None
        
        char = self.content[self.pos]
        self.pos += 1
        
        # Update line/column tracking
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace characters (spaces and tabs, not newlines)."""
        while self.peek() in (' ', '\t'):
            self.advance()
    
    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire input into a list of tokens.
        
        Returns:
            List of tokens including position information
        """
        tokens = []
        
        while self.pos < len(self.content):
            token = self._next_token()
            if token:
                tokens.append(token)
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        
        return tokens
    
    def _next_token(self) -> Optional[Token]:
        """Get the next token from the input."""
        # Skip whitespace (spaces and tabs, not newlines)
        self.skip_whitespace()
        
        if self.pos >= len(self.content):
            return None
        
        start_line = self.line
        start_col = self.column
        char = self.peek()
        
        # Newline
        if char == '\n':
            self.advance()
            return Token(TokenType.NEWLINE, '\n', start_line, start_col)
        
        # Handle \r\n or \r as newline
        if char == '\r':
            self.advance()
            if self.peek() == '\n':
                self.advance()
            return Token(TokenType.NEWLINE, '\n', start_line, start_col)
        
        # Comment
        if char == '#':
            return self._scan_comment(start_line, start_col)
        
        # Colon
        if char == ':':
            self.advance()
            return Token(TokenType.COLON, ':', start_line, start_col)
        
        # Left bracket
        if char == '[':
            self.advance()
            return Token(TokenType.LBRACKET, '[', start_line, start_col)
        
        # Right bracket
        if char == ']':
            self.advance()
            return Token(TokenType.RBRACKET, ']', start_line, start_col)
        
        # Comma
        if char == ',':
            self.advance()
            return Token(TokenType.COMMA, ',', start_line, start_col)
        
        # Quoted string
        if char in ('"', "'"):
            return self._scan_string(start_line, start_col)
        
        # Key (identifier before colon)
        if char.isalpha() or char == '_':
            return self._scan_key(start_line, start_col)
        
        # Unexpected character
        raise AFSyntaxError(
            f"Unexpected character: {char!r}",
            filename=self.filename,
            line=start_line,
            column=start_col
        )
    
    def _scan_comment(self, start_line: int, start_col: int) -> Token:
        """Scan a comment from # to end of line."""
        value = []
        self.advance()  # Skip #
        
        while self.peek() and self.peek() not in ('\n', '\r'):
            value.append(self.advance())
        
        return Token(TokenType.COMMENT, ''.join(value), start_line, start_col)
    
    def _scan_string(self, start_line: int, start_col: int) -> Token:
        """
        Scan a quoted string with escape sequence handling.
        
        Supports:
        - Single and double quotes
        - Multiline strings (preserving embedded newlines)
        - Escape sequences: \\", \\', \\\\, \\n, \\t
        """
        quote_char = self.advance()  # Consume opening quote
        value = []
        
        while True:
            char = self.peek()
            
            if char is None:
                raise AFSyntaxError(
                    f"Unterminated string (missing closing {quote_char})",
                    filename=self.filename,
                    line=start_line,
                    column=start_col
                )
            
            # Allow actual newlines inside strings (multiline support)
            if char == '\n' or char == '\r':
                # Preserve the newline character in the string value
                value.append(self.advance())
                continue
            
            if char == '\\':
                self.advance()
                next_char = self.peek()
                
                if next_char is None:
                    raise AFSyntaxError(
                        "Incomplete escape sequence at end of input",
                        filename=self.filename,
                        line=self.line,
                        column=self.column
                    )
                
                # Handle escape sequences
                if next_char == quote_char:
                    value.append(quote_char)
                    self.advance()
                elif next_char == '\\':
                    value.append('\\')
                    self.advance()
                elif next_char == 'n':
                    value.append('\n')
                    self.advance()
                elif next_char == 't':
                    value.append('\t')
                    self.advance()
                else:
                    # Keep backslash for unknown escapes
                    value.append('\\')
            elif char == quote_char:
                self.advance()  # Consume closing quote
                break
            else:
                value.append(self.advance())
        
        string_value = ''.join(value)
        
        # Empty string check
        if not string_value:
            raise AFEmptyValueError(
                "String value cannot be empty",
                filename=self.filename,
                line=start_line,
                column=start_col
            )
        
        return Token(TokenType.STRING, string_value, start_line, start_col)
    
    def _scan_key(self, start_line: int, start_col: int) -> Token:
        """Scan an identifier (key name)."""
        value = []
        
        while self.peek() and (self.peek().isalnum() or self.peek() in ('_', '-')):
            value.append(self.advance())
        
        return Token(TokenType.KEY, ''.join(value), start_line, start_col)


class Parser:
    """
    State machine parser that consumes tokens to build the .af structure.
    
    Maintains v1.0 compatibility while supporting the flat purpose/vision/must/dont/nice
    schema with deterministic ordering.
    """
    
    def __init__(self, tokens: List[Token], filename: str = None, source_lines: List[str] = None):
        self.tokens = tokens
        self.filename = filename
        self.source_lines = source_lines or []
        self.pos = 0
        self.result = {}
        self.seen_keys = {}  # Track where each key was first seen
    
    def _get_source_line(self, line_num: int) -> Optional[str]:
        """Get the source line for error reporting (1-indexed)."""
        if self.source_lines and 0 < line_num <= len(self.source_lines):
            return self.source_lines[line_num - 1]
        return None
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at token at current position + offset."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self) -> Optional[Token]:
        """Consume and return current token."""
        if self.pos >= len(self.tokens):
            return None
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Consume token of expected type or raise error."""
        token = self.peek()
        if token is None or token.type != token_type:
            expected = token_type.name
            actual = token.type.name if token else "EOF"
            
            raise AFSyntaxError(
                f"Expected {expected}, got {actual}",
                filename=self.filename,
                line=token.line if token else self.tokens[-1].line,
                column=token.column if token else self.tokens[-1].column
            )
        return self.advance()
    
    def skip_newlines_and_comments(self):
        """Skip any newline and comment tokens."""
        while self.peek() and self.peek().type in (TokenType.NEWLINE, TokenType.COMMENT):
            self.advance()
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse tokens into the .af structure.
        
        Returns:
            Dictionary with keys in canonical order: purpose, vision, must, dont, nice
        """
        while self.peek() and self.peek().type != TokenType.EOF:
            self.skip_newlines_and_comments()
            
            if self.peek() and self.peek().type != TokenType.EOF:
                self._parse_line()
        
        # Verify all required keys are present
        missing_keys = REQUIRED_KEYS - set(self.result.keys())
        if missing_keys:
            # Use the last token's position for error reporting
            last_token = self.tokens[-2] if len(self.tokens) > 1 else self.tokens[0]
            raise AFMissingKeyError(
                f"Missing required keys: {', '.join(sorted(missing_keys))}",
                filename=self.filename,
                line=last_token.line
            )
        
        # Return result in canonical order
        return {key: self.result[key] for key in CANONICAL_KEY_ORDER}
    
    def _parse_line(self):
        """Parse a single key-value line."""
        # Expect key
        key_token = self.peek()
        
        # If we hit EOF or newline/comment, return
        if not key_token or key_token.type in (TokenType.EOF, TokenType.NEWLINE, TokenType.COMMENT):
            return
        
        if key_token.type != TokenType.KEY:
            # Unexpected token - check for common cases
            if key_token.type == TokenType.COLON:
                raise AFSyntaxError(
                    "Empty key before ':'",
                    filename=self.filename,
                    line=key_token.line,
                    column=key_token.column
                )
            else:
                raise AFSyntaxError(
                    f"Expected key, got {key_token.type.name}",
                    filename=self.filename,
                    line=key_token.line,
                    column=key_token.column
                )
        
        self.advance()
        key = key_token.value.lower()
        
        # Check for unknown keys
        if key not in REQUIRED_KEYS:
            # Find closest match
            suggestion = _find_closest_key(key, REQUIRED_KEYS)
            error_msg = f"Unknown key '{key}'"
            if suggestion:
                error_msg += f" (did you mean '{suggestion}'?)"
            raise AFUnknownKeyError(
                error_msg,
                filename=self.filename,
                line=key_token.line,
                column=key_token.column,
                source_line=self._get_source_line(key_token.line)
            )
        
        # Check for duplicate keys
        if key in self.result:
            raise AFDuplicateKeyError(
                f"Duplicate key '{key}' (first seen on line {self.seen_keys[key]})",
                filename=self.filename,
                line=key_token.line,
                column=key_token.column
            )
        
        # Expect colon
        self.expect(TokenType.COLON)
        
        # Parse value based on key type
        if key in STRING_KEYS:
            value = self._parse_string_value()
        elif key in LIST_KEYS:
            value = self._parse_list_value()
        else:
            raise AFParseError(
                f"Unknown key type for '{key}'",
                filename=self.filename,
                line=key_token.line
            )
        
        # Store result
        self.result[key] = value
        self.seen_keys[key] = key_token.line
        
        # Skip to end of line
        self.skip_newlines_and_comments()
    
    def _parse_string_value(self) -> str:
        """Parse a string value (for purpose/vision)."""
        token = self.peek()
        
        if not token or token.type != TokenType.STRING:
            # Check if we got a KEY token (unquoted string)
            if token and token.type == TokenType.KEY:
                raise AFSyntaxError(
                    f"String value must be quoted (use \" or ')",
                    filename=self.filename,
                    line=token.line,
                    column=token.column
                )
            raise AFSyntaxError(
                "Expected string value",
                filename=self.filename,
                line=token.line if token else self.tokens[-1].line,
                column=token.column if token else self.tokens[-1].column
            )
        
        self.advance()
        
        # Check for stray tokens after string
        next_token = self.peek()
        if next_token and next_token.type not in (TokenType.NEWLINE, TokenType.COMMENT, TokenType.EOF):
            raise AFSyntaxError(
                f"Unexpected characters after string value",
                filename=self.filename,
                line=next_token.line,
                column=next_token.column
            )
        
        return token.value
    
    def _parse_list_value(self) -> List[str]:
        """Parse a list value (for must/dont/nice)."""
        # Expect opening bracket
        bracket_token = self.peek()
        if not bracket_token or bracket_token.type != TokenType.LBRACKET:
            # Check if we got unquoted text instead
            if bracket_token and bracket_token.type in (TokenType.KEY, TokenType.STRING):
                raise AFSyntaxError(
                    "List must start with '['",
                    filename=self.filename,
                    line=bracket_token.line,
                    column=bracket_token.column
                )
            raise AFSyntaxError(
                "Expected list value starting with '['",
                filename=self.filename,
                line=bracket_token.line if bracket_token else self.tokens[-1].line,
                column=bracket_token.column if bracket_token else self.tokens[-1].column
            )
        
        self.advance()
        
        items = []
        expecting_item = True  # Track if we expect an item (after [ or ,)
        
        while True:
            # Skip any whitespace/newlines (though single-line for v1.0)
            while self.peek() and self.peek().type in (TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
            
            token = self.peek()
            
            # Check for closing bracket
            if token and token.type == TokenType.RBRACKET:
                # Empty list check
                if not items and expecting_item:
                    # We just saw [ and now ]
                    break  # Will be handled below
                # Trailing comma is OK (not expecting_item would be False if we just parsed an item)
                break
            
            # Check for comma when expecting an item (empty item)
            if token and token.type == TokenType.COMMA and expecting_item:
                raise AFSyntaxError(
                    "Empty item in list (consecutive commas or missing value)",
                    filename=self.filename,
                    line=token.line,
                    column=token.column
                )
            
            # Expect string
            if not token or token.type != TokenType.STRING:
                # Check if we got an unquoted identifier
                if token and token.type == TokenType.KEY:
                    raise AFSyntaxError(
                        "List items must be quoted strings",
                        filename=self.filename,
                        line=token.line,
                        column=token.column
                    )
                if not items:
                    raise AFEmptyValueError(
                        "List cannot be empty",
                        filename=self.filename,
                        line=token.line if token else self.tokens[-1].line,
                        column=token.column if token else self.tokens[-1].column
                    )
                raise AFSyntaxError(
                    "Expected string in list",
                    filename=self.filename,
                    line=token.line if token else self.tokens[-1].line,
                    column=token.column if token else self.tokens[-1].column
                )
            
            self.advance()
            items.append(token.value)
            expecting_item = False
            
            # Skip whitespace
            while self.peek() and self.peek().type in (TokenType.NEWLINE, TokenType.COMMENT):
                self.advance()
            
            # Check for comma or closing bracket
            next_token = self.peek()
            if next_token and next_token.type == TokenType.COMMA:
                self.advance()
                expecting_item = True  # Now we expect another item
            elif next_token and next_token.type == TokenType.RBRACKET:
                break
            else:
                raise AFSyntaxError(
                    "Expected comma or closing bracket in list",
                    filename=self.filename,
                    line=next_token.line if next_token else self.tokens[-1].line,
                    column=next_token.column if next_token else self.tokens[-1].column
                )
        
        # Expect closing bracket
        closing_bracket = self.peek()
        if not closing_bracket or closing_bracket.type != TokenType.RBRACKET:
            raise AFSyntaxError(
                "List must end with ']'",
                filename=self.filename,
                line=closing_bracket.line if closing_bracket else self.tokens[-1].line,
                column=closing_bracket.column if closing_bracket else self.tokens[-1].column
            )
        self.advance()
        
        if not items:
            raise AFEmptyValueError(
                "List cannot be empty",
                filename=self.filename,
                line=closing_bracket.line,
                column=closing_bracket.column
            )
        
        # Check for stray tokens after list
        next_token = self.peek()
        if next_token and next_token.type not in (TokenType.NEWLINE, TokenType.COMMENT, TokenType.EOF):
            raise AFSyntaxError(
                f"Unexpected characters after list",
                filename=self.filename,
                line=next_token.line,
                column=next_token.column
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
        AFSizeError: When file exceeds 1MB limit
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
            filename=filepath,
            line=1
        )
    
    # Load content with size and encoding validation
    content = load_input(source=filepath)
    
    # Tokenize
    tokenizer = Tokenizer(content, filename=filepath)
    tokens = tokenizer.tokenize()
    
    # Parse
    parser = Parser(tokens, filename=filepath, source_lines=tokenizer.lines)
    result = parser.parse()
    
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
    # Check size limit BEFORE stripping BOM to ensure consistency with load_input
    if len(content.encode('utf-8')) > MAX_INPUT_SIZE:
        raise AFSizeError(
            f"Input too large: exceeds {MAX_INPUT_SIZE} bytes (1MB) limit",
            filename=filename
        )
    
    # Strip UTF-8 BOM if present
    content = _strip_utf8_bom(content)
    
    # Tokenize
    tokenizer = Tokenizer(content, filename=filename)
    tokens = tokenizer.tokenize()
    
    # Parse
    parser = Parser(tokens, filename=filename, source_lines=tokenizer.lines)
    result = parser.parse()
    
    return result


def parse_af_stdin() -> Dict[str, Any]:
    """
    Parse .af content from stdin.
    
    Returns:
        Dictionary with normalized lowercase keys and typed values
        
    Raises:
        AFParseError and subclasses for validation errors
        AFSizeError: When input exceeds 1MB limit
    """
    # Check size on raw bytes before any text decoding/normalization
    if hasattr(sys.stdin, 'buffer'):
        # Read raw bytes from buffer to check size before normalization
        try:
            # Read all available bytes to check actual size
            raw_bytes = sys.stdin.buffer.read()
            if len(raw_bytes) > MAX_INPUT_SIZE:
                raise AFSizeError(
                    f"Input too large: exceeds {MAX_INPUT_SIZE} bytes (1MB) limit"
                )
            
            # Decode bytes to string with UTF-8 encoding
            try:
                content = raw_bytes.decode('utf-8', errors='strict')
            except UnicodeDecodeError as e:
                raise AFParseError(f"Input must be UTF-8 encoded: {e}")
        except Exception as e:
            # Re-raise our exceptions as-is
            if isinstance(e, (AFSizeError, AFParseError)):
                raise
            # Wrap other exceptions
            raise AFParseError(f"Error reading from stdin: {e}")
    else:
        # Fallback for cases where stdin doesn't have a buffer (e.g., StringIO in tests)
        # In test environments, we can use load_input directly
        content = load_input(stream=sys.stdin)
    
    # Strip BOM if present
    content = _strip_utf8_bom(content)
    
    # Tokenize
    tokenizer = Tokenizer(content, filename="<stdin>")
    tokens = tokenizer.tokenize()
    
    # Parse
    parser = Parser(tokens, filename="<stdin>", source_lines=tokenizer.lines)
    result = parser.parse()
    
    return result
