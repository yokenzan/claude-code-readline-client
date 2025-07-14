# Claude Code Readline Client (CCRC)

A Python-based CLI client for Claude Code that provides GNU Readline functionality, improving the user experience with features like command history, tab completion, and keyboard shortcuts.

## Overview

The current Claude Code CLI lacks advanced line editing capabilities. This project creates a wrapper that maintains all Claude Code functionality while adding Readline support for a better user experience.

## Features

### Core Features
- Accept user input via GNU Readline interface
- Send prompts to Claude Code via SDK and display responses
- Maintain conversation context across multiple interactions
- Support multi-line input for complex prompts
- Handle streaming responses from Claude Code

### Readline Features
- Command history persistence across sessions
- Tab completion for common commands and file paths
- Keyboard shortcuts (Ctrl+A, Ctrl+E, Ctrl+K, etc.)
- History search with Ctrl+R
- Customizable key bindings via .inputrc

### Enhanced Features
- Custom commands (e.g., /help, /clear, /history, /exit)
- Syntax highlighting for code blocks in responses
- Save/load conversation sessions
- Export conversation to markdown
- Configuration file support for default options

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd readline-claude-code

# Install dependencies with uv
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

## Usage

```bash
# Basic usage
ccrc

# With custom config
ccrc --config ~/.ccrc_config.yaml

# One-shot mode
ccrc --prompt "Explain this code: $(cat main.py)"
```

## Configuration

Create a configuration file at `~/.ccrc_config.yaml`:

```yaml
history:
  file: ~/.ccrc_history
  size: 10000

display:
  syntax_highlighting: true
  theme: monokai
  wrap_text: true

claude:
  model: claude-3-opus-20240229
  max_turns: 10
  allowed_tools:
    - Read
    - Write
    - Bash
  permission_mode: acceptEdits

completions:
  - "import numpy as np"
  - "import pandas as pd"
  - "def main():"
```

## Development

This project uses trace-based development with GitHub issues and pull requests. See the [comprehensive requirements and technical specifications](comprehensive-requirements-and-technical-specifications.md) for detailed information.

## Requirements

- Python 3.8+
- claude-code-sdk-python
- GNU Readline library
- Cross-platform support (Linux, macOS, Windows with WSL)

## License

GPL-3.0 (To comply with GNU Readline's GPL license)