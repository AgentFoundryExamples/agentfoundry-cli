# Agent Foundry CLI

Command-line interface for Agent Foundry, providing the `af` command for managing and running agent workflows.

## Features

- 🚀 Built with [Typer](https://typer.tiangolo.com/) for an intuitive CLI experience
- 📦 Easy installation via pip
- 🎨 Rich terminal output with color support
- 🔌 Extensible command structure for future features

## Installation

### From Source (Development)

1. Clone the repository:
```bash
git clone https://github.com/AgentFoundryExamples/agentfoundry-cli.git
cd agentfoundry-cli
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in editable mode with development dependencies:
```bash
pip install -e ".[dev]"
```

### From PyPI (Future)

Once published:
```bash
pip install agentfoundry-cli
```

## Usage

After installation, the `af` command will be available:

```bash
# Display help
af --help

# Say hello (example command)
af hello

# Display version
af version
```

### Alternative Invocation

You can also run the CLI as a Python module:
```bash
python -m agentfoundry_cli --help
```

Or directly for local development:
```bash
python agentfoundry_cli/cli.py --help
```

## Upcoming Features

- **`af run`** command for executing agent workflows (coming soon!)
- Additional commands for agent management and configuration

## Avoiding Conflicts

If you have an existing `af` binary in your PATH, use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
which af  # Should point to your venv
```

## Terminal Color Support

The CLI uses Typer's rich output by default. In environments without color support, output remains legible as Typer gracefully degrades to plain text.

## Documentation

For development and contribution guidelines, see [docs/development.md](docs/development.md).



# Permanents (License, Contributing, Author)

Do not change any of the below sections

## License

All Agent Foundry work is licensed under the GPLv3 License - see the LICENSE file for details.

## Contributing

Feel free to submit issues and enhancement requests!

## Author

Created by Agent Foundry and John Brosnihan
