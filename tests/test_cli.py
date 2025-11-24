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
Basic tests for the Agent Foundry CLI.
"""

from typer.testing import CliRunner
from agentfoundry_cli.cli import app
from agentfoundry_cli import __version__

runner = CliRunner(mix_stderr=False)


def test_help_command():
    """Test that the help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Agent Foundry CLI" in result.stdout
    assert "Commands" in result.stdout


def test_hello_command_default():
    """Test hello command without name option."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello from Agent Foundry CLI!" in result.stdout
    assert "af run" in result.stdout


def test_hello_command_with_name():
    """Test hello command with name option."""
    result = runner.invoke(app, ["hello", "--name", "TestUser"])
    assert result.exit_code == 0
    assert "Hello, TestUser!" in result.stdout


def test_version_command():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
    assert "Agent Foundry CLI version" in result.stdout


def test_version_format():
    """Test that version follows semantic versioning format."""
    import re
    # Check version format is semantic versioning (e.g., 0.1.0, 1.2.3)
    assert re.match(r"^\d+\.\d+\.\d+$", __version__)


def test_run_command_stub():
    """Test that run command exists and requires an argument."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0  # Should exit with error since no file provided
    # Verify it's asking for the file argument
    output = result.stdout.lower() + (result.stderr.lower() if result.stderr else "")
    assert "missing" in output or "required" in output or "file" in output


def test_run_command_in_help():
    """Test that run command appears in main help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout.lower()
    # The new description mentions parsing and validating .af files
    assert ".af" in result.stdout.lower() or "parse" in result.stdout.lower()

