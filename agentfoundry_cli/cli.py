"""
Main CLI module for Agent Foundry CLI.

This module defines the Typer application and all CLI commands.
"""

import typer
from typing import Optional
from agentfoundry_cli import __version__

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
    typer.echo("\n[Upcoming Feature] 'af run' command will be available soon!")


@app.command()
def run():
    """
    Run an agent workflow (coming soon).
    
    This command will execute agent workflows based on configuration files.
    Currently under development.
    """
    typer.echo("⚠️  The 'run' command is not yet implemented.")
    typer.echo("This feature is coming soon and will execute agent workflows.")
    raise typer.Exit(1)


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
