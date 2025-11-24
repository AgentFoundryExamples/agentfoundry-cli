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
Tests for the `af run` CLI command.
"""

import json
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner
from agentfoundry_cli.cli import app

runner = CliRunner(mix_stderr=False)


# Valid .af file content for testing
VALID_AF_CONTENT = """
purpose: "Build a task management system"
vision: "Create an intuitive tool for tracking tasks"
must: ["Complete authentication", "Implement data persistence"]
dont: ["Skip error handling", "Ignore security"]
nice: ["Add dark mode", "Support mobile devices"]
"""


def test_run_command_with_valid_file():
    """Test af run with a valid .af file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        
        # Verify canonical key order
        keys = list(output_data.keys())
        assert keys == ['purpose', 'vision', 'must', 'dont', 'nice']
        
        # Verify content
        assert output_data['purpose'] == "Build a task management system"
        assert output_data['vision'] == "Create an intuitive tool for tracking tasks"
        assert output_data['must'] == ["Complete authentication", "Implement data persistence"]
        assert output_data['dont'] == ["Skip error handling", "Ignore security"]
        assert output_data['nice'] == ["Add dark mode", "Support mobile devices"]
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_example_file():
    """Test af run with the examples/example.af file."""
    example_path = Path(__file__).parent.parent / "examples" / "example.af"
    
    if example_path.exists():
        result = runner.invoke(app, ["run", str(example_path)])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        
        # Verify canonical key order
        keys = list(output_data.keys())
        assert keys == ['purpose', 'vision', 'must', 'dont', 'nice']
        
        # Verify structure
        assert isinstance(output_data['purpose'], str)
        assert isinstance(output_data['vision'], str)
        assert isinstance(output_data['must'], list)
        assert isinstance(output_data['dont'], list)
        assert isinstance(output_data['nice'], list)


def test_run_command_json_only_stdout():
    """Test that stdout contains only JSON, no extra logs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Verify stdout is valid JSON (no extra text)
        output_data = json.loads(result.stdout)
        assert output_data is not None
        
        # Verify stderr is empty for successful run
        assert result.stderr == "" or not result.stderr
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_missing_file():
    """Test af run with a non-existent file."""
    result = runner.invoke(app, ["run", "/nonexistent/path/file.af"])
    
    # Check exit code
    assert result.exit_code == 1
    
    # Verify error message is in output (Typer may route to stdout or stderr)
    output = result.stdout + (result.stderr or "")
    assert "not found" in output.lower()
    assert "nonexistent" in output.lower() or "file.af" in output.lower()


def test_run_command_with_directory():
    """Test af run with a directory path instead of a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        result = runner.invoke(app, ["run", temp_dir])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message
        output = result.stdout + (result.stderr or "")
        assert "error" in output.lower()


def test_run_command_with_wrong_extension():
    """Test af run with a file that doesn't have .af extension."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message
        output = result.stdout + (result.stderr or "")
        assert ".af extension" in output.lower() or "extension" in output.lower()
        assert ".txt" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_missing_required_key():
    """Test af run with a file missing a required key."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
"""
    # Missing 'nice' key
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message
        output = result.stdout + (result.stderr or "")
        assert "missing" in output.lower()
        assert "nice" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_duplicate_key():
    """Test af run with a file containing duplicate keys."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
purpose: "Duplicate purpose"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message
        output = result.stdout + (result.stderr or "")
        assert "duplicate" in output.lower()
        assert "purpose" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_syntax_error():
    """Test af run with a file containing syntax errors."""
    content = """
purpose: Build a task manager
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    # 'purpose' value is not quoted - syntax error
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message contains line information
        output = result.stdout + (result.stderr or "")
        assert "error" in output.lower()
        assert "line" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_empty_list():
    """Test af run with a file containing empty list."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
must: []
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message
        output = result.stdout + (result.stderr or "")
        assert "empty" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_crlf_line_endings():
    """Test af run with a file containing CRLF line endings."""
    content = "purpose: \"Build a task manager\"\r\nvision: \"Create something great\"\r\nmust: [\"Complete auth\"]\r\ndont: [\"Skip tests\"]\r\nnice: [\"Add themes\"]\r\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8', newline='') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code - should succeed
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert output_data['purpose'] == "Build a task manager"
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_trailing_whitespace():
    """Test af run with a file containing trailing whitespace."""
    content = """
purpose: "Build a task manager"   
vision: "Create something great"  
must: ["Complete auth"]  
dont: ["Skip tests"]  
nice: ["Add themes"]  
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code - should succeed
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert output_data['purpose'] == "Build a task manager"
        
    finally:
        os.unlink(temp_path)


def test_run_command_with_large_list():
    """Test af run with a file containing large lists (hundreds of entries)."""
    large_list_items = [f"\"Item {i}\"" for i in range(200)]
    large_list = "[" + ", ".join(large_list_items) + "]"
    
    content = f"""
purpose: "Build a task manager"
vision: "Create something great"
must: {large_list}
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert len(output_data['must']) == 200
        assert output_data['must'][0] == "Item 0"
        assert output_data['must'][199] == "Item 199"
        
    finally:
        os.unlink(temp_path)


def test_run_command_help():
    """Test af run --help displays help text."""
    result = runner.invoke(app, ["run", "--help"])
    
    # Check exit code
    assert result.exit_code == 0
    
    # Verify help text
    assert "Parse and validate" in result.stdout
    assert ".af file" in result.stdout
    assert "FILE" in result.stdout or "file" in result.stdout.lower()


def test_run_command_treats_help_af_as_filename():
    """Test that af run help.af treats help.af as a filename, not a help command."""
    content = VALID_AF_CONTENT
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Rename to help.af
        help_path = os.path.join(os.path.dirname(temp_path), "help.af")
        os.rename(temp_path, help_path)
        
        result = runner.invoke(app, ["run", help_path])
        
        # Check exit code - should parse the file
        assert result.exit_code == 0
        
        # Parse JSON output
        output_data = json.loads(result.stdout)
        assert output_data['purpose'] == "Build a task management system"
        
        os.unlink(help_path)
        
    except:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'help_path' in locals() and os.path.exists(help_path):
            os.unlink(help_path)
        raise


def test_run_command_error_includes_filename():
    """Test that error messages include the filename."""
    content = """
purpose: "Build a task manager"
unknown_key: "This should fail"
vision: "Create something great"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message includes filename
        output = result.stdout + (result.stderr or "")
        assert os.path.basename(temp_path) in output or temp_path in output
        
    finally:
        os.unlink(temp_path)


def test_run_command_error_includes_line_number():
    """Test that error messages include line numbers."""
    content = """
purpose: "Build a task manager"
vision: "Create something great"
unknown_key: "This should fail"
must: ["Complete auth"]
dont: ["Skip tests"]
nice: ["Add themes"]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 1
        
        # Verify error message includes line number
        output = result.stdout + (result.stderr or "")
        assert "line" in output.lower()
        
    finally:
        os.unlink(temp_path)


def test_run_command_without_arguments():
    """Test af run without any arguments shows error."""
    result = runner.invoke(app, ["run"])
    
    # Check exit code
    assert result.exit_code != 0
    
    # Verify error message in stdout or stderr
    output = result.stdout + (result.stderr or "")
    assert "missing" in output.lower() or "required" in output.lower()


def test_run_command_json_is_valid():
    """Test that output is always valid JSON for successful runs."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Check exit code
        assert result.exit_code == 0
        
        # Verify JSON is valid (will raise exception if not)
        json_data = json.loads(result.stdout)
        
        # Verify it's a dictionary
        assert isinstance(json_data, dict)
        
        # Verify all expected keys are present
        assert set(json_data.keys()) == {'purpose', 'vision', 'must', 'dont', 'nice'}
        
    finally:
        os.unlink(temp_path)


def test_run_command_stdout_stderr_separation():
    """Test that stdout contains only JSON and stderr contains errors."""
    # Test successful case - stdout should have JSON, stderr should be empty
    with tempfile.NamedTemporaryFile(mode='w', suffix='.af', delete=False, encoding='utf-8') as f:
        f.write(VALID_AF_CONTENT)
        temp_path = f.name
    
    try:
        result = runner.invoke(app, ["run", temp_path])
        
        # Successful run
        assert result.exit_code == 0
        
        # stdout should be valid JSON
        json.loads(result.stdout)
        
        # Test error case - errors should go to stderr, stdout should be empty
        result_error = runner.invoke(app, ["run", "/nonexistent.af"])
        assert result_error.exit_code == 1
        
        # Assert stderr contains the error message
        assert result_error.stderr, "stderr should not be empty for error case"
        assert "error" in result_error.stderr.lower() or "not found" in result_error.stderr.lower(), \
            "stderr should contain error message"
        
        # Assert stdout is empty or has no content in error case
        assert not result_error.stdout or result_error.stdout.strip() == "", \
            "stdout should be empty for error case to keep it clean for piping"
        
    finally:
        os.unlink(temp_path)
