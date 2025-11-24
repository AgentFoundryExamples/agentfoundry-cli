"""
Basic tests for the Agent Foundry CLI.
"""

from typer.testing import CliRunner
from agentfoundry_cli.cli import app
from agentfoundry_cli import __version__

runner = CliRunner()


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


def test_version_import():
    """Test that version can be imported."""
    assert __version__ == "0.1.0"
