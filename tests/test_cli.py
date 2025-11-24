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


def test_version_format():
    """Test that version follows semantic versioning format."""
    import re
    # Check version format is semantic versioning (e.g., 0.1.0, 1.2.3)
    assert re.match(r"^\d+\.\d+\.\d+$", __version__)


def test_run_command_stub():
    """Test that run command stub exists and provides informative message."""
    result = runner.invoke(app, ["run"])
    assert result.exit_code == 1  # Should exit with error since not implemented
    assert "not yet implemented" in result.stdout
    assert "coming soon" in result.stdout.lower()


def test_run_command_in_help():
    """Test that run command appears in main help output."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.stdout.lower()
    assert "workflow" in result.stdout.lower()

