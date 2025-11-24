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
Tests for the Agent Foundry .af file parser.
"""

import pytest
import tempfile
import os
import sys
from pathlib import Path

from agentfoundry_cli.parser import (
    parse_af_file,
    validate_af_content,
    AFParseError,
    AFMissingKeyError,
    AFDuplicateKeyError,
    AFUnknownKeyError,
    AFSyntaxError,
    AFEmptyValueError,
)


# Test constants for size limit testing
TEST_SIZE_SAFETY_MARGIN = 100  # Safety margin to stay under limit
TEST_SIZE_SMALL_EXCESS = 1  # Small amount over limit for boundary testing
TEST_SIZE_LARGE_EXCESS = 10000  # Large amount over limit for clear rejection
TEST_SIZE_MEDIUM_EXCESS = 1000  # Medium amount over limit


# Valid .af file content for testing
VALID_AF_CONTENT = """
purpose: "Build a task management system"
vision: "Create an intuitive tool for tracking tasks"
must: ["Complete authentication", "Implement data persistence"]
dont: ["Skip error handling", "Ignore security"]
nice: ["Add dark mode", "Support mobile devices"]
"""


def test_parse_valid_file():
    """Test parsing a valid .af file."""
    result = validate_af_content(VALID_AF_CONTENT)
    
    assert isinstance(result, dict)
    assert result['purpose'] == "Build a task management system"
    assert result['vision'] == "Create an intuitive tool for tracking tasks"
    assert result['must'] == ["Complete authentication", "Implement data persistence"]
    assert result['dont'] == ["Skip error handling", "Ignore security"]
    assert result['nice'] == ["Add dark mode", "Support mobile devices"]


def test_parse_valid_file_with_single_quotes():
    """Test parsing strings with single quotes."""
    content = """
purpose: 'Build a task management system'
vision: 'Create an intuitive tool for tracking tasks'
must: ['Complete authentication', 'Implement data persistence']
dont: ['Skip error handling', 'Ignore security']
nice: ['Add dark mode', 'Support mobile devices']
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "Build a task management system"
    assert result['vision'] == "Create an intuitive tool for tracking tasks"


def test_parse_with_apostrophes():
    """Test parsing strings containing apostrophes."""
    content = """
purpose: "It's a task manager"
vision: "We'll build something great"
must: ["Don't skip tests", "It's important to document"]
dont: ["Don't forget validation"]
nice: ["We'd like dark mode"]
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "It's a task manager"
    assert result['vision'] == "We'll build something great"
    assert result['must'] == ["Don't skip tests", "It's important to document"]
    assert result['dont'] == ["Don't forget validation"]
    assert result['nice'] == ["We'd like dark mode"]


def test_parse_with_escaped_quotes():
    """Test parsing strings with escaped quotes."""
    content = """
purpose: "Say \\"hello\\" to users"
vision: "It's called \\"TaskMaster\\""
must: ["Handle \\"special\\" cases"]
dont: ["Forget \\"edge cases\\""]
nice: ["Support \\"themes\\""]
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == 'Say "hello" to users'
    assert result['vision'] == 'It\'s called "TaskMaster"'
    assert result['must'] == ['Handle "special" cases']


def test_case_insensitive_keys():
    """Test that keys are case-insensitive."""
    content = """
PURPOSE: "Build a task manager"
Vision: "Create something great"
MuSt: ["Complete auth"]
DONT: ["Skip tests"]
Nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    # All keys should be lowercase in result
    assert 'purpose' in result
    assert 'vision' in result
    assert 'must' in result
    assert 'dont' in result
    assert 'nice' in result


def test_whitespace_tolerance():
    """Test tolerance for various whitespace."""
    content = """
  purpose  :   "Build a task manager"  
     vision:"Create something great"
must   :   ["Complete auth"]   
dont:["Skip tests"]
nice:     ["Add themes"]     
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "Build a task manager"
    assert result['vision'] == "Create something great"


def test_empty_lines_and_comments():
    """Test that empty lines and comments are ignored."""
    content = """
# This is a comment
purpose: "Build a task manager"

# Another comment
vision: "Create something great"

must: ["Complete auth"]
# Comment in the middle
dont: ["Skip tests"]

nice: ["Add themes"]
# Final comment
"""
    result = validate_af_content(content)
    
    assert len(result) == 5
    assert result['purpose'] == "Build a task manager"


def test_missing_purpose_key():
    """Test error when purpose key is missing."""
    content = """
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "purpose" in str(exc_info.value).lower()


def test_missing_vision_key():
    """Test error when vision key is missing."""
    content = """
purpose: "Build a task manager"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "vision" in str(exc_info.value).lower()


def test_missing_must_key():
    """Test error when must key is missing."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "must" in str(exc_info.value).lower()


def test_missing_dont_key():
    """Test error when dont key is missing."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
nice: ["Add themes"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "dont" in str(exc_info.value).lower()


def test_missing_nice_key():
    """Test error when nice key is missing."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "nice" in str(exc_info.value).lower()


def test_duplicate_key_error():
    """Test error when a key appears multiple times."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
purpose: "Duplicate purpose"
"""
    with pytest.raises(AFDuplicateKeyError) as exc_info:
        validate_af_content(content)
    
    assert "duplicate" in str(exc_info.value).lower()
    assert "purpose" in str(exc_info.value).lower()
    assert "line 2" in str(exc_info.value).lower()


def test_duplicate_key_different_case():
    """Test error when duplicate keys have different casing."""
    content = """
purpose: "Build a task manager"
PURPOSE: "Duplicate purpose"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFDuplicateKeyError) as exc_info:
        validate_af_content(content)
    
    assert "duplicate" in str(exc_info.value).lower()
    assert "purpose" in str(exc_info.value).lower()


def test_unknown_key_error():
    """Test error when an unknown key is encountered."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
unknown: "This should fail"
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    assert "unknown" in str(exc_info.value).lower()


def test_empty_string_value():
    """Test error when a string value is empty."""
    content = """
purpose: ""
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFEmptyValueError) as exc_info:
        validate_af_content(content)
    
    assert "empty" in str(exc_info.value).lower()


def test_empty_list_value():
    """Test error when a list value is empty."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: []
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFEmptyValueError) as exc_info:
        validate_af_content(content)
    
    assert "empty" in str(exc_info.value).lower()


def test_unquoted_string_value():
    """Test error when string value is not quoted."""
    content = """
purpose: Build a task manager
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "quoted" in str(exc_info.value).lower()


def test_unterminated_string():
    """Test error for unterminated string."""
    content = """
purpose: "Build a task manager
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "unterminated" in str(exc_info.value).lower()


def test_mismatched_quotes():
    """Test error for mismatched quotes."""
    content = """
purpose: "Build a task manager'
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "unterminated" in str(exc_info.value).lower() or "closing" in str(exc_info.value).lower()


def test_list_without_brackets():
    """Test error when list doesn't have brackets."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: "Complete auth", "More stuff"
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "[" in str(exc_info.value) or "list" in str(exc_info.value).lower()


def test_list_missing_closing_bracket():
    """Test error when list is missing closing bracket."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "]" in str(exc_info.value) or "list" in str(exc_info.value).lower()


def test_list_with_unquoted_items():
    """Test error when list items are not quoted."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: [Complete auth, More stuff]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "quoted" in str(exc_info.value).lower()


def test_trailing_comma_in_list():
    """Test that trailing commas in lists are handled gracefully."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth", "More stuff",]
dont: ["Skip tests",]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['must'] == ["Complete auth", "More stuff"]
    assert result['dont'] == ["Skip tests"]


def test_empty_list_item_rejected():
    """Test that empty items in lists are rejected."""
    # Empty item in middle
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth", , "More stuff"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "empty item" in str(exc_info.value).lower()


def test_empty_list_item_at_start_rejected():
    """Test that empty item at start of list is rejected."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: [, "Complete auth", "More stuff"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "empty item" in str(exc_info.value).lower()


def test_multiple_consecutive_commas_rejected():
    """Test that multiple consecutive commas are rejected."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth",, , "More stuff"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "empty item" in str(exc_info.value).lower()


def test_stray_characters_after_string():
    """Test error for stray characters after quoted string."""
    content = """
purpose: "Build a task manager" extra
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "unexpected" in str(exc_info.value).lower() or "after" in str(exc_info.value).lower()


def test_missing_colon_separator():
    """Test error when line is missing colon separator."""
    content = """
purpose "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert ":" in str(exc_info.value)


def test_empty_key():
    """Test error when key is empty."""
    content = """
: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    assert "empty key" in str(exc_info.value).lower()


def test_utf8_bom_handling():
    """Test that UTF-8 BOM is properly handled."""
    # UTF-8 BOM is '\ufeff'
    content = "\ufeff" + VALID_AF_CONTENT
    result = validate_af_content(content)
    
    assert result['purpose'] == "Build a task management system"
    assert len(result) == 5


def test_parse_file_with_path():
    """Test parsing from actual file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = parse_af_file(temp_path)
        
        assert result['purpose'] == "Build a task management system"
        assert result['vision'] == "Create an intuitive tool for tracking tasks"
        assert len(result['must']) == 2
        assert len(result['dont']) == 2
        assert len(result['nice']) == 2
    finally:
        os.unlink(temp_path)


def test_parse_nonexistent_file():
    """Test error when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        parse_af_file("/nonexistent/path/file.af")


def test_parse_file_requires_af_extension():
    """Test that parser rejects files without .af extension."""
    # Create a file with .txt extension
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        with pytest.raises(AFParseError) as exc_info:
            parse_af_file(temp_path)
        
        assert ".af extension" in str(exc_info.value).lower()
        assert ".txt" in str(exc_info.value)
        # Verify filename is included in the error
        assert temp_path in str(exc_info.value) or exc_info.value.filename == temp_path
    finally:
        os.unlink(temp_path)


def test_parse_file_requires_extension():
    """Test that parser rejects files with no extension."""
    # Create a file with no extension
    with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        with pytest.raises(AFParseError) as exc_info:
            parse_af_file(temp_path)
        
        assert ".af extension" in str(exc_info.value).lower()
        # Verify filename is included in the error
        assert temp_path in str(exc_info.value) or exc_info.value.filename == temp_path
    finally:
        os.unlink(temp_path)


def test_parse_file_accepts_uppercase_af_extension():
    """Test that parser accepts .AF extension (case-insensitive)."""
    # Create a file with .AF extension (uppercase)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.AF', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = parse_af_file(temp_path)
        
        assert result['purpose'] == "Build a task management system"
        assert len(result) == 5
    finally:
        os.unlink(temp_path)


def test_error_includes_filename():
    """Test that errors include filename in message."""
    content = """
purpose: "Build a task manager"
unknown: "This should fail"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content, filename="test.af")
    
    assert "test.af" in str(exc_info.value)


def test_error_includes_line_number():
    """Test that errors include line number in message."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
unknown: "This should fail"
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content, filename="test.af")
    
    error_msg = str(exc_info.value)
    assert "line 5" in error_msg.lower()


def test_multiline_strings_supported():
    """Test that multiline strings are now supported with newlines preserved."""
    content = """
purpose: "This is a
multiline string"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    
    # Should parse successfully
    result = validate_af_content(content)
    # Newline should be preserved in the output
    assert result['purpose'] == "This is a\nmultiline string"


def test_list_with_mixed_quotes():
    """Test list with mixed single and double quotes."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth", 'Implement tests']
dont: ['Skip tests', "Ignore security"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['must'] == ["Complete auth", "Implement tests"]
    assert result['dont'] == ["Skip tests", "Ignore security"]


def test_single_item_list():
    """Test list with single item."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['must'] == ["Complete auth"]
    assert isinstance(result['must'], list)


def test_list_with_whitespace():
    """Test list parsing with various whitespace."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: [  "Complete auth"  ,  "More stuff"  ]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['must'] == ["Complete auth", "More stuff"]


def test_keys_returned_lowercase():
    """Test that all keys in result are lowercase."""
    content = """
PURPOSE: "Build a task manager"
VISION: "Create something great"
MUST: ["Complete auth"]
DONT: ["Skip tests"]
NICE: ["Add themes"]
"""
    result = validate_af_content(content)
    
    for key in result.keys():
        assert key.islower()


def test_string_with_newline_escape():
    """Test string with newline escape sequence."""
    content = """
purpose: "First line\\nSecond line"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "First line\nSecond line"


def test_string_with_tab_escape():
    """Test string with tab escape sequence."""
    content = """
purpose: "Column1\\tColumn2"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "Column1\tColumn2"


def test_comprehensive_valid_file():
    """Test a comprehensive valid file with all features."""
    content = """
# Configuration for task manager
purpose: "Build a comprehensive task management system"
vision: "Create an intuitive and powerful tool for tracking team tasks"

# Required features
must: ["User authentication", "Task creation and editing", "Data persistence"]

# Things to avoid
dont: ["Skip input validation", "Ignore security best practices", "Forget error handling"]

# Nice to have features
nice: ["Dark mode support", "Mobile responsive design", "Real-time updates"]
"""
    result = validate_af_content(content)
    
    assert len(result) == 5
    assert isinstance(result['purpose'], str)
    assert isinstance(result['vision'], str)
    assert isinstance(result['must'], list)
    assert isinstance(result['dont'], list)
    assert isinstance(result['nice'], list)
    assert len(result['must']) == 3
    assert len(result['dont']) == 3
    assert len(result['nice']) == 3


def test_utf8_with_emojis():
    """Test that UTF-8 emojis parse without truncation."""
    content = """
purpose: "Build a task manager 🚀"
vision: "Create something great 🎯✨"
must: ["Authentication 🔐", "Database 💾"]
dont: ["Skip tests 🚫"]
nice: ["Dark mode 🌙"]
"""
    result = validate_af_content(content)
    
    assert result['purpose'] == "Build a task manager 🚀"
    assert result['vision'] == "Create something great 🎯✨"
    assert result['must'] == ["Authentication 🔐", "Database 💾"]
    assert result['dont'] == ["Skip tests 🚫"]
    assert result['nice'] == ["Dark mode 🌙"]


def test_utf8_with_combining_characters():
    """Test that combining characters parse correctly."""
    # Combining diacriticals and other complex Unicode
    content = """
purpose: "Café système with naïve approach"
vision: "Über cool 日本語 中文"
must: ["Test α β γ", "مرحبا العالم"]
dont: ["Skip ñ ü ö"]
nice: ["Support 한글"]
"""
    result = validate_af_content(content)
    
    assert "Café" in result['purpose']
    assert "naïve" in result['purpose']
    assert "Über" in result['vision']
    assert "日本語" in result['vision']
    assert "α β γ" in result['must'][0]


def test_utf8_bom_at_file_start():
    """Test that UTF-8 BOM at file start is stripped."""
    # UTF-8 BOM is '\ufeff'
    content = "\ufeff" + VALID_AF_CONTENT
    result = validate_af_content(content)
    
    assert result['purpose'] == "Build a task management system"
    assert len(result) == 5


def test_size_limit_exactly_1mb_minus_1():
    """Test that files just under 1MB parse successfully."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE
    
    # Create content that's close to but under 1MB
    base_content = """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    # Calculate how much padding we need
    base_size = len(base_content.encode('utf-8'))
    # Leave room for the base content plus safety margin
    padding_size = MAX_INPUT_SIZE - base_size - TEST_SIZE_SAFETY_MARGIN
    padding = "# " + "x" * padding_size + "\n"
    
    content = padding + base_content
    
    # Verify size is under limit
    assert len(content.encode('utf-8')) < MAX_INPUT_SIZE
    
    # Should parse successfully
    result = validate_af_content(content)
    assert result['purpose'] == "Test"


def test_size_limit_exactly_1mb_accepted():
    """Test that input exactly at 1MB (1,048,576 bytes) is accepted."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE
    
    # Create content that's exactly 1MB
    base_content = """purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    # Calculate padding needed to reach exactly 1MB
    base_size = len(base_content.encode('utf-8'))
    remaining = MAX_INPUT_SIZE - base_size
    
    # Add padding comments to fill to exactly 1MB
    # Each comment line is "# x\n" = 4 bytes
    num_comment_lines = remaining // 4
    padding = ("# x\n" * num_comment_lines)
    
    # Add any remaining bytes as a final comment (without newline if needed)
    remaining_bytes = remaining % 4
    if remaining_bytes > 0:
        # Build the final comment to exactly fill the remaining bytes
        padding += ('#' + ' x'[:remaining_bytes - 1])
    
    content = padding + base_content
    
    # Verify size is exactly at limit
    actual_size = len(content.encode('utf-8'))
    assert actual_size == MAX_INPUT_SIZE, f"Expected {MAX_INPUT_SIZE}, got {actual_size}"
    
    # Should parse successfully
    result = validate_af_content(content)
    assert result['purpose'] == "Test"


def test_size_limit_over_1mb_rejected():
    """Test that input over 1MB (1,048,577+ bytes) is rejected."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE, AFSizeError
    
    # Create content that's over 1MB by 1 byte
    base_content = """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    # Create padding to exceed 1MB
    padding_size = MAX_INPUT_SIZE - len(base_content.encode('utf-8')) + TEST_SIZE_SMALL_EXCESS
    padding = "# " + "x" * padding_size + "\n"
    
    content = padding + base_content
    
    # Verify size is over limit
    assert len(content.encode('utf-8')) > MAX_INPUT_SIZE
    
    # Should be rejected
    with pytest.raises(AFSizeError) as exc_info:
        validate_af_content(content)
    
    assert "too large" in str(exc_info.value).lower()
    assert "1mb" in str(exc_info.value).lower() or "1048576" in str(exc_info.value)


def test_size_limit_exceeds_1mb_rejected():
    """Test that input exceeding 1MB is rejected."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE, AFSizeError
    
    # Create content larger than 1MB
    base_content = """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    # Create padding significantly over 1MB
    padding_size = MAX_INPUT_SIZE + TEST_SIZE_LARGE_EXCESS
    padding = "# " + "x" * padding_size + "\n"
    
    content = padding + base_content
    
    # Should be rejected
    with pytest.raises(AFSizeError) as exc_info:
        validate_af_content(content)
    
    assert "too large" in str(exc_info.value).lower()


def test_empty_file_rejected():
    """Test that completely empty file is rejected."""
    content = ""
    
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "missing" in str(exc_info.value).lower()


def test_file_with_only_comments_rejected():
    """Test that file with only comments is rejected."""
    content = """
# This is just a comment
# Another comment
# No actual content
"""
    
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "missing" in str(exc_info.value).lower()


def test_file_with_only_whitespace_rejected():
    """Test that file with only whitespace is rejected."""
    content = "\n\n   \n\t\n   \n"
    
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    assert "missing" in str(exc_info.value).lower()


def test_stdin_support():
    """Test that parse_af_stdin works correctly."""
    import io
    from agentfoundry_cli.parser import parse_af_stdin
    
    # Temporarily replace stdin
    old_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(VALID_AF_CONTENT)
        result = parse_af_stdin()
        
        assert result['purpose'] == "Build a task management system"
        assert result['vision'] == "Create an intuitive tool for tracking tasks"
        assert len(result['must']) == 2
    finally:
        sys.stdin = old_stdin


def test_stdin_size_limit():
    """Test that stdin input exceeding 1MB is rejected."""
    import io
    from agentfoundry_cli.parser import parse_af_stdin, MAX_INPUT_SIZE, AFSizeError
    
    # Create content larger than 1MB
    padding_size = MAX_INPUT_SIZE + TEST_SIZE_MEDIUM_EXCESS
    padding = "# " + "x" * padding_size + "\n"
    content = padding + """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    
    old_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(content)
        
        with pytest.raises(AFSizeError) as exc_info:
            parse_af_stdin()
        
        assert "too large" in str(exc_info.value).lower()
    finally:
        sys.stdin = old_stdin


def test_file_size_check_before_parse():
    """Test that file size is checked before attempting to parse."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE, AFSizeError
    
    # Create a large file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        # Write content larger than 1MB
        padding_size = MAX_INPUT_SIZE + TEST_SIZE_MEDIUM_EXCESS
        f.write("# " + "x" * padding_size + "\n")
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        with pytest.raises(AFSizeError) as exc_info:
            parse_af_file(temp_path)
        
        assert "too large" in str(exc_info.value).lower()
        # Verify the error mentions the file size
        assert str(MAX_INPUT_SIZE) in str(exc_info.value) or "1MB" in str(exc_info.value).upper()
    finally:
        os.unlink(temp_path)


def test_load_input_requires_exactly_one_source():
    """Test that load_input requires exactly one of source or stream."""
    from agentfoundry_cli.parser import load_input
    
    # Neither source nor stream
    with pytest.raises(ValueError):
        load_input()
    
    # Both source and stream
    import io
    with pytest.raises(ValueError):
        load_input(source="test.af", stream=io.StringIO("test"))


def test_tokenizer_preserves_positions():
    """Test that tokenizer tracks line and column positions correctly."""
    from agentfoundry_cli.parser import Tokenizer, TokenType
    
    content = """purpose: "test"
vision: "test2"
"""
    tokenizer = Tokenizer(content)
    tokens = tokenizer.tokenize()
    
    # Find the purpose key token
    purpose_token = [t for t in tokens if t.type == TokenType.KEY and t.value == "purpose"][0]
    assert purpose_token.line == 1
    assert purpose_token.column == 1
    
    # Find the vision key token
    vision_token = [t for t in tokens if t.type == TokenType.KEY and t.value == "vision"][0]
    assert vision_token.line == 2
    assert vision_token.column == 1


def test_error_messages_include_position():
    """Test that error messages include precise line and column information."""
    content = """
purpose: "test"
unknown_key: "value"
vision: "test"
must: ["test"]
dont: ["test"]
nice: ["test"]
"""
    
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include line number
    assert "line 3" in error_msg.lower()
    # New tokenizer includes column info
    assert "column" in error_msg.lower()


def test_multiline_strings_preserve_newlines():
    """Test that multiline strings preserve newlines in output."""
    content = """
purpose: "This is a
multiline string"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    
    # Should parse successfully with newlines preserved
    result = validate_af_content(content)
    assert result['purpose'] == "This is a\nmultiline string"


def test_canonical_key_order_preserved():
    """Test that parser always returns keys in canonical order regardless of input order."""
    from agentfoundry_cli.parser import CANONICAL_KEY_ORDER
    
    # Test 1: Keys in canonical order
    content1 = """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    result1 = validate_af_content(content1)
    assert list(result1.keys()) == CANONICAL_KEY_ORDER
    
    # Test 2: Keys in random order
    content2 = """
nice: ["Test"]
must: ["Test"]
vision: "Test"
purpose: "Test"
dont: ["Test"]
"""
    result2 = validate_af_content(content2)
    assert list(result2.keys()) == CANONICAL_KEY_ORDER
    
    # Test 3: Keys in reverse order
    content3 = """
nice: ["Test"]
dont: ["Test"]
must: ["Test"]
vision: "Test"
purpose: "Test"
"""
    result3 = validate_af_content(content3)
    assert list(result3.keys()) == CANONICAL_KEY_ORDER
    
    # Verify all results have same key order
    assert list(result1.keys()) == list(result2.keys()) == list(result3.keys())


def test_parse_af_file_canonical_order():
    """Test that parse_af_file returns keys in canonical order."""
    from agentfoundry_cli.parser import CANONICAL_KEY_ORDER
    
    # Create a file with keys in non-canonical order
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write("""
dont: ["Skip tests"]
nice: ["Add themes"]
purpose: "Build a task manager"
must: ["Complete auth"]
vision: "Create something great"
""")
        temp_path = f.name
    
    try:
        result = parse_af_file(temp_path)
        # Verify keys are in canonical order
        assert list(result.keys()) == CANONICAL_KEY_ORDER
        
        # Verify values are correct
        assert result['purpose'] == "Build a task manager"
        assert result['vision'] == "Create something great"
        assert result['must'] == ["Complete auth"]
        assert result['dont'] == ["Skip tests"]
        assert result['nice'] == ["Add themes"]
    finally:
        os.unlink(temp_path)


def test_validate_af_content_bom_size_consistency():
    """Test that size limit includes BOM bytes for consistency with load_input."""
    from agentfoundry_cli.parser import MAX_INPUT_SIZE, AFSizeError
    
    # BOM is 3 bytes in UTF-8
    bom = '\ufeff'
    bom_size = len(bom.encode('utf-8'))
    
    # Create content that is exactly at limit when BOM is included
    base_content = 'purpose: "T"\nvision: "T"\nmust: ["T"]\ndont: ["T"]\nnice: ["T"]\n'
    target_size_without_bom = MAX_INPUT_SIZE - bom_size
    
    # Build content to reach exact size
    padding_needed = target_size_without_bom - len(base_content.encode('utf-8'))
    content_without_bom = ('# x\n' * (padding_needed // 4)) + base_content
    
    # Fine-tune to exact size
    while len(content_without_bom.encode('utf-8')) < target_size_without_bom:
        content_without_bom = '#\n' + content_without_bom
    while len(content_without_bom.encode('utf-8')) > target_size_without_bom:
        content_without_bom = content_without_bom[1:]
    
    # Add BOM - total should be exactly at limit
    content_with_bom = bom + content_without_bom
    assert len(content_with_bom.encode('utf-8')) == MAX_INPUT_SIZE
    
    # Should parse successfully (at limit)
    result = validate_af_content(content_with_bom)
    assert result['purpose'] == 'T'
    
    # Add one more byte - should be rejected
    content_over_limit = content_with_bom + 'x'
    assert len(content_over_limit.encode('utf-8')) > MAX_INPUT_SIZE
    
    with pytest.raises(AFSizeError) as exc_info:
        validate_af_content(content_over_limit)
    
    assert "too large" in str(exc_info.value).lower()


def test_stdin_size_check_before_newline_normalization():
    """Test that stdin size check uses raw bytes before CRLF normalization."""
    from agentfoundry_cli.parser import parse_af_stdin, MAX_INPUT_SIZE, AFSizeError
    import io
    
    # Create content with CRLF that exceeds limit in raw bytes
    # but would be under limit after LF normalization
    base = 'purpose: "T"\r\nvision: "T"\r\nmust: ["T"]\r\ndont: ["T"]\r\nnice: ["T"]\r\n'
    padding = "# comment line\r\n"
    
    # Calculate how many padding lines we need to exceed 1MB
    num_lines = (MAX_INPUT_SIZE - len(base.encode('utf-8'))) // len(padding.encode('utf-8')) + 100
    content_crlf = (padding * num_lines) + base
    
    # Verify our test setup
    size_crlf = len(content_crlf.encode('utf-8'))
    size_lf = len(content_crlf.replace('\r\n', '\n').encode('utf-8'))
    assert size_crlf > MAX_INPUT_SIZE, "CRLF version should exceed limit"
    assert size_lf < MAX_INPUT_SIZE, "LF version should be under limit"
    
    # Mock stdin with a buffer
    class MockStdin:
        def __init__(self, buffer):
            self.buffer = buffer
    
    old_stdin = sys.stdin
    try:
        stdin_buffer = io.BytesIO(content_crlf.encode('utf-8'))
        sys.stdin = MockStdin(stdin_buffer)
        
        # Should be rejected based on raw byte count (CRLF)
        with pytest.raises(AFSizeError) as exc_info:
            parse_af_stdin()
        
        assert "too large" in str(exc_info.value).lower()
    finally:
        sys.stdin = old_stdin


def test_multiline_list_with_newlines():
    """Test that lists can span multiple lines with newlines between items."""
    content = """
purpose: "Test"
vision: "Test"
must: [
    "Item 1",
    "Item 2",
    "Item 3"
]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2", "Item 3"]


def test_multiline_list_trailing_comma():
    """Test that lists accept trailing commas before closing bracket."""
    content = """
purpose: "Test"
vision: "Test"
must: [
    "Item 1",
    "Item 2",
    "Item 3",
]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2", "Item 3"]


def test_inline_comment_after_value():
    """Test that inline comments after values are ignored."""
    content = """
purpose: "Build a task manager" # This is a comment
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a task manager"


def test_inline_comment_after_list():
    """Test that inline comments after lists are ignored."""
    content = """
purpose: "Test"
vision: "Test"
must: ["Item 1", "Item 2"] # Comment after list
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2"]


def test_inline_comment_in_list():
    """Test that comments can appear within multiline lists."""
    content = """
purpose: "Test"
vision: "Test"
must: [
    "Item 1",  # First item
    "Item 2",  # Second item
    "Item 3"   # Third item
]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2", "Item 3"]


def test_fuzzy_matching_typo_purpose():
    """Test that fuzzy matching suggests correct key for typo."""
    content = """
pourpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value).lower()
    assert "pourpose" in error_msg
    assert "did you mean" in error_msg
    assert "purpose" in error_msg


def test_fuzzy_matching_typo_vision():
    """Test fuzzy matching for vision typo."""
    content = """
purpose: "Test"
vission: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value).lower()
    assert "vission" in error_msg
    assert "did you mean" in error_msg
    assert "vision" in error_msg


def test_fuzzy_matching_typo_must():
    """Test fuzzy matching for must typo."""
    content = """
purpose: "Test"
vision: "Test"
muts: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value).lower()
    assert "muts" in error_msg
    assert "did you mean" in error_msg
    assert "must" in error_msg


def test_fuzzy_matching_no_suggestion_far_typo():
    """Test that very different keys don't get suggestions."""
    content = """
purpose: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
completely_wrong: "Test"
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value).lower()
    assert "completely_wrong" in error_msg
    # Should not have a suggestion since it's too far
    assert "did you mean" not in error_msg


def test_multiline_purpose_with_vision():
    """Test multiline purpose string."""
    content = """
purpose: "Build a comprehensive
task management system
that is easy to use"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a comprehensive\ntask management system\nthat is easy to use"


def test_multiline_vision():
    """Test multiline vision string."""
    content = """
purpose: "Test"
vision: "Create an intuitive
and powerful tool"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['vision'] == "Create an intuitive\nand powerful tool"


def test_mixed_multiline_strings_and_lists():
    """Test combination of multiline strings and multiline lists."""
    content = """
purpose: "Build a comprehensive
task management system"
vision: "Create an intuitive
and powerful tool"
must: [
    "Authentication",
    "Data persistence"
]
dont: ["Skip tests"]
nice: ["Dark mode"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a comprehensive\ntask management system"
    assert result['vision'] == "Create an intuitive\nand powerful tool"
    assert result['must'] == ["Authentication", "Data persistence"]


def test_error_with_caret_indicator():
    """Test that errors include caret indicators pointing to the problem."""
    content = """
purpose: "Test"
unknwon: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFUnknownKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include the source line
    assert "unknwon" in error_msg
    # Should include caret indicator
    assert "^" in error_msg


def test_newline_separated_items_without_commas():
    """Test that list items can be separated by newlines without commas (P1 fix)."""
    content = """
purpose: "Test"
vision: "Test"
must: [
    "Item 1"
    "Item 2"
    "Item 3"
]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2", "Item 3"]


def test_newline_separated_with_mixed_commas():
    """Test that list items can mix newlines and commas."""
    content = """
purpose: "Test"
vision: "Test"
must: [
    "Item 1",
    "Item 2"
    "Item 3"
]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2", "Item 3"]


def test_duplicate_key_error_has_caret(capsys):
    """Test that duplicate key errors include caret indicator (P2 fix)."""
    content = """
purpose: "Test"
purpose: "Duplicate"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFDuplicateKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    # Should include the source line
    assert 'purpose: "Duplicate"' in error_msg


def test_empty_key_error_has_caret():
    """Test that empty key errors include caret indicator (P2 fix)."""
    content = """
: "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    # Should include the source line
    assert ': "Test"' in error_msg


def test_unquoted_string_error_has_caret():
    """Test that unquoted string errors include caret indicator (P2 fix)."""
    content = """
purpose: Build a task manager
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "quoted" in error_msg.lower()


def test_same_line_items_without_comma_rejected():
    """Test that items on the same line without comma are rejected (P2 fix)."""
    content = """
purpose: "Test"
vision: "Test"
must: ["Item 1" "Item 2"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value).lower()
    # Should require comma or closing bracket
    assert "comma" in error_msg or "bracket" in error_msg


def test_unterminated_string_has_caret():
    """Test that unterminated string errors include caret indicator (P1 fix)."""
    content = """
purpose: "This is unterminated
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "unterminated" in error_msg.lower()


def test_empty_string_tokenizer_error_has_caret():
    """Test that empty string errors from tokenizer include caret indicator (P1 fix)."""
    content = """
purpose: ""
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFEmptyValueError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "empty" in error_msg.lower()


def test_missing_colon_has_caret():
    """Test that missing colon errors include caret indicator (P1 fix)."""
    content = """
purpose "Test"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFSyntaxError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "colon" in error_msg.lower() or "expected" in error_msg.lower()


def test_comment_before_string_value():
    """Test that comments before string values are ignored (P1 fix)."""
    content = """
purpose: # This is a comment
"Build a task manager"
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a task manager"


def test_comment_before_list_value():
    """Test that comments before list values are ignored (P1 fix)."""
    content = """
purpose: "Test"
vision: "Test"
must: # Comment before list
["Item 1", "Item 2"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['must'] == ["Item 1", "Item 2"]


def test_newline_before_value():
    """Test that newlines before values are ignored."""
    content = """
purpose:
"Build a task manager"
vision: "Test"
must:
["Item 1"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a task manager"
    assert result['must'] == ["Item 1"]


def test_multiple_comments_before_value():
    """Test that multiple comments/newlines before values are ignored."""
    content = """
purpose: # Comment 1
# Comment 2
"Build a task manager"
vision: "Test"
must: # Comment
# Another comment
["Item 1", "Item 2"]
dont: ["Test"]
nice: ["Test"]
"""
    result = validate_af_content(content)
    assert result['purpose'] == "Build a task manager"
    assert result['must'] == ["Item 1", "Item 2"]


def test_missing_key_has_caret():
    """Test that missing key errors include caret indicator (P1 fix)."""
    content = """
vision: "Test"
must: ["Test"]
dont: ["Test"]
nice: ["Test"]
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "missing" in error_msg.lower()
    assert "purpose" in error_msg.lower()


def test_missing_multiple_keys_has_caret():
    """Test that missing multiple keys error includes caret indicator."""
    content = """
vision: "Test"
"""
    with pytest.raises(AFMissingKeyError) as exc_info:
        validate_af_content(content)
    
    error_msg = str(exc_info.value)
    # Should include caret indicator
    assert "^" in error_msg
    assert "missing" in error_msg.lower()
