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


def test_multiline_not_supported():
    """Test that multiline values are not supported (should fail)."""
    content = """
purpose: "Build a task manager
that spans multiple lines"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    with pytest.raises(AFSyntaxError):
        validate_af_content(content)


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
