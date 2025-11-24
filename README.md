# Agent Foundry CLI

Command-line interface for Agent Foundry, providing the `af` command for managing and running agent workflows.

## Features

- 🚀 Built with [Typer](https://typer.tiangolo.com/) for an intuitive CLI experience
- 📦 Easy installation via pip
- 🎨 Rich terminal output with color support
- 🔌 Extensible command structure for future features
- 📝 Parser and validator for `.af` (Agent Foundry) configuration files

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

# Parse and validate an Agent Foundry file
af run examples/example.af

# Say hello (example command)
af hello

# Display version
af version
```

### Running Agent Foundry Files

The `af run` command parses and validates `.af` files, outputting canonical JSON:

```bash
af run examples/example.af
```

The command will:
- Validate the file has a `.af` extension
- Parse and validate the syntax and structure
- Output canonical JSON with ordered keys to stdout
- Exit with code 0 on success, non-zero on errors
- Display human-readable error messages with filename and line numbers on stderr

Example output:
```json
{
  "purpose": "Build a comprehensive task management system",
  "vision": "Create an intuitive and powerful tool for tracking team tasks and projects",
  "must": [
    "User authentication and authorization",
    "Task creation, editing, and deletion",
    "Data persistence with database",
    "Input validation and error handling"
  ],
  "dont": [
    "Skip security best practices",
    "Ignore input validation",
    "Forget error handling",
    "Deploy without testing"
  ],
  "nice": [
    "Dark mode support",
    "Mobile responsive design",
    "Real-time collaboration",
    "Email notifications",
    "Advanced search and filtering"
  ]
}
```

You can pipe the output to other tools like `jq`:
```bash
af run examples/example.af | jq '.purpose'
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

- Additional commands for agent management and configuration
- Integration with agent execution platforms

## Agent Foundry Files

Agent Foundry uses `.af` files to define agent configurations. These files specify:

- **purpose** - What the agent should accomplish
- **vision** - The desired outcome or end state
- **must** - Required behaviors and constraints
- **dont** - Behaviors to avoid
- **nice** - Optional enhancements

Example `.af` file:

```
purpose: "Build a task management system"
vision: "Create an intuitive tool for tracking tasks"
must: ["User authentication", "Data persistence"]
dont: ["Skip error handling", "Ignore security"]
nice: ["Dark mode", "Mobile support"]
```

For detailed syntax and format specification, see [docs/format.md](docs/format.md). A complete example is available in [examples/example.af](examples/example.af).

### Using the Parser

```python
from agentfoundry_cli.parser import parse_af_file

config = parse_af_file("agent.af")
print(config['purpose'])  # Access parsed values
```

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
