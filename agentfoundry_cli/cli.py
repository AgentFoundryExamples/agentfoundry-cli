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
Main CLI module for Agent Foundry CLI.

This module defines the Typer application and all CLI commands.
"""

import typer
import sys
import json
from typing import Optional
from pathlib import Path
from agentfoundry_cli import __version__
from agentfoundry_cli.parser import parse_af_file, parse_af_stdin, AFParseError, AFSizeError

# Canonical key order for JSON output
CANONICAL_KEY_ORDER = ['purpose', 'vision', 'must', 'dont', 'nice']


# Create the main Typer app
app = typer.Typer(
    name="af",
    help="Agent Foundry CLI - Command-line interface for Agent Foundry",
    add_completion=True,
    rich_markup_mode="rich",
)


@app.command()
def hello(
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Name to greet",
    )
):
    """
    Say hello - a simple placeholder command.
    
    This is a placeholder demonstrating the CLI structure.
    """
    if name:
        typer.echo(f"Hello, {name}!")
    else:
        typer.echo("Hello from Agent Foundry CLI!")
    typer.echo("\nUse 'af run <file>' to parse .af files, or 'af --help' for more commands.")


@app.command()
def run(
    file: str = typer.Argument(
        ...,
        help="Path to the .af file to parse and validate, or '-' to read from stdin",
        metavar="FILE"
    )
):
    """
    Parse and validate an Agent Foundry (.af) file.
    
    Reads the specified .af file, validates its syntax and structure,
    and outputs the parsed configuration as canonical JSON to stdout.
    
    Use '-' to read from stdin instead of a file.
    
    Examples:
        af run examples/example.af
        cat example.af | af run -
        echo '...' | af run -
    """
    try:
        if file == '-':
            # Read from stdin
            result = parse_af_stdin()
        else:
            # Parse the file
            result = parse_af_file(file)
        
        # Create ordered JSON output with canonical key order
        ordered_output = {key: result[key] for key in CANONICAL_KEY_ORDER}
        
        # Output JSON to stdout
        json_output = json.dumps(ordered_output, indent=2, ensure_ascii=False)
        typer.echo(json_output)
        
    except FileNotFoundError:
        typer.secho(f"Error: File not found: {file}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except AFSizeError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except AFParseError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def validate(
    file: str = typer.Argument(
        ...,
        help="Path to the .af file to validate, or '-' to read from stdin",
        metavar="FILE"
    )
):
    """
    Validate an Agent Foundry (.af) file without output.
    
    Runs the same parser as 'af run' but suppresses stdout on success.
    Errors are written to stderr. Exit code 0 indicates valid input,
    non-zero indicates validation failure.
    
    Ideal for CI/CD pipelines where only the exit code matters.
    
    Examples:
        af validate examples/example.af
        cat example.af | af validate -
        af validate config.af && echo "Valid!"
    """
    try:
        if file == '-':
            # Read from stdin
            parse_af_stdin()
        else:
            # Parse the file
            parse_af_file(file)
        
        # Success - exit silently with code 0
        raise typer.Exit(0)
        
    except FileNotFoundError:
        typer.secho(f"Error: File not found: {file}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except AFSizeError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except AFParseError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    except typer.Exit:
        raise
    except Exception as e:
        typer.secho(f"Unexpected error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)


@app.command()
def help(
    command: Optional[str] = typer.Argument(
        None,
        help="Command to get help for"
    )
):
    """
    Display help for the CLI or a specific command.
    
    Examples:
        af help        # Show main help
        af help run    # Show help for 'run' command
    """
    # Get the Click app from Typer
    click_app = typer.main.get_command(app)
    
    if command is None:
        # Show main help
        ctx = click_app.make_context('af', [])
        typer.echo(click_app.get_help(ctx))
    else:
        # Find and show help for specific command
        ctx = click_app.make_context('af', [])
        subcommand = click_app.commands.get(command)
        
        if subcommand is None:
            typer.secho(f"Error: Unknown command '{command}'", fg=typer.colors.RED, err=True)
            typer.echo("\nAvailable commands:")
            for cmd_name in sorted(click_app.commands.keys()):
                typer.echo(f"  - {cmd_name}")
            raise typer.Exit(1)
        
        # Show help for the subcommand - use resilient_parsing to avoid validation
        sub_ctx = subcommand.make_context(
            command, 
            [], 
            parent=ctx,
            allow_extra_args=True,
            allow_interspersed_args=False,
            resilient_parsing=True
        )
        typer.echo(subcommand.get_help(sub_ctx))


@app.command()
def version():
    """
    Display the version of the Agent Foundry CLI.
    """
    typer.echo(f"Agent Foundry CLI version: {__version__}")


def main():
    """
    Main entry point for the CLI application.
    
    This function is called when running 'af' command or 'python -m agentfoundry_cli'.
    """
    app()


# Allow direct execution: python agentfoundry_cli/cli.py
if __name__ == "__main__":
    main()
