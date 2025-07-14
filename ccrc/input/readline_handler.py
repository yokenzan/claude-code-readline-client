"""
GNU Readline input handler for CCRC.
"""

import os
from typing import Optional, List, Callable, Any


def _import_readline_library(
    prefer_gnureadline: bool = False, prefer_rl: bool = False
) -> Any:
    """
    Import readline library with preference for specific libraries if available.

    Args:
        prefer_gnureadline: If True, try to import gnureadline first
        prefer_rl: If True, try to import rl library first

    Returns:
        Imported readline module
    """
    readline_lib = None
    library_name = "unknown"

    # Try rl library first if preferred
    if prefer_rl:
        try:
            import rl.readline as readline_lib

            library_name = "rl"
        except ImportError:
            pass

    # Try gnureadline if preferred and rl not found
    if readline_lib is None and prefer_gnureadline:
        try:
            import gnureadline as readline_lib

            library_name = "gnureadline"
        except ImportError:
            pass

    # Fall back to standard readline
    if readline_lib is None:
        try:
            import readline as readline_lib

            library_name = "readline"
        except ImportError:
            raise ImportError(
                "No readline library available. Install readline, gnureadline, or rl."
            )

    print(f"Using {library_name} library")
    return readline_lib


class ReadlineInputHandler:
    """Handles GNU Readline input with history and key bindings."""

    def __init__(
        self,
        history_file: Optional[str] = None,
        history_size: int = 10000,
        prefer_gnureadline: bool = False,
        prefer_rl: bool = False,
    ):
        """
        Initialize readline input handler.

        Args:
            history_file: Path to history file (default: ~/.ccrc_history)
            history_size: Maximum number of history entries
            prefer_gnureadline: If True, prefer gnureadline over standard readline
            prefer_rl: If True, prefer rl library over other options
        """
        self.history_file = history_file or os.path.expanduser("~/.ccrc_history")
        self.history_size = history_size
        self.completer_function: Optional[Callable] = None
        self.prefer_gnureadline = prefer_gnureadline
        self.prefer_rl = prefer_rl

        # Import readline library
        self.readline = _import_readline_library(prefer_gnureadline, prefer_rl)

        # Initialize readline
        self._setup_readline()

    def _setup_readline(self):
        """Configure minimal readline settings - let GNU Readline handle defaults."""
        # Set history size
        self.readline.set_history_length(self.history_size)

        # Load history if file exists
        if os.path.exists(self.history_file):
            try:
                self.readline.read_history_file(self.history_file)
            except PermissionError:
                print(f"Warning: Cannot read history file {self.history_file}")
            except Exception as e:
                print(f"Warning: Error reading history file: {e}")

        # Load user's .inputrc if available (before any other settings)
        inputrc_path = os.path.expanduser("~/.inputrc")
        if os.path.exists(inputrc_path):
            try:
                self.readline.read_init_file(inputrc_path)
            except Exception as e:
                print(f"Warning: Error reading .inputrc: {e}")

        # Configure tab completion delimiters
        self.readline.set_completer_delims(" \t\n`!@#$%^&*()=+[{]}\\|;:'\",<>?")

        # Enable tab completion (GNU Readline default behavior)
        self.readline.parse_and_bind("tab: complete")

        # Try to enable advanced GNU Readline commands if available
        self._try_enable_advanced_commands()

    def _try_enable_advanced_commands(self):
        """Try to enable advanced GNU Readline commands if the library supports them."""
        advanced_commands = [
            (
                '"\\C-x\\C-e": edit-and-execute-command',
                "C-x C-e (edit-and-execute-command)",
            ),
            ('"\\C-x*": glob-expand-word', "C-x * (glob-expand-word)"),
            ('"\\eg": glob-complete-word', "M-g (glob-complete-word)"),
        ]

        enabled_commands = []
        for binding, description in advanced_commands:
            try:
                self.readline.parse_and_bind(binding)
                enabled_commands.append(description)
            except Exception:
                # Command not available in this readline implementation
                pass

        if enabled_commands:
            print(f"Enabled advanced commands: {', '.join(enabled_commands)}")

    def set_completer(self, completer_function: Callable):
        """
        Set custom tab completion function.

        Args:
            completer_function: Function that takes (text, state) and returns
                completion
        """
        self.completer_function = completer_function
        self.readline.set_completer(completer_function)

    def get_input(self, prompt: str = "> ") -> str:
        """
        Get input from user with readline support.

        Args:
            prompt: Input prompt string

        Returns:
            User input string

        Raises:
            KeyboardInterrupt: When user presses Ctrl+C
            EOFError: When user presses Ctrl+D
        """
        try:
            user_input = input(prompt)

            # Add non-empty input to history
            if user_input.strip():
                self.readline.add_history(user_input)

            return user_input

        except KeyboardInterrupt:
            print()  # New line after ^C
            raise
        except EOFError:
            print()  # New line after ^D
            raise

    def get_multiline_input(
        self, prompt: str = "> ", continuation_prompt: str = "... "
    ) -> str:
        """
        Get multi-line input with backslash continuation.

        Args:
            prompt: Initial prompt string
            continuation_prompt: Continuation prompt string

        Returns:
            Complete multi-line input string
        """
        lines = []
        current_prompt = prompt

        while True:
            try:
                line = self.get_input(current_prompt)

                # Check for backslash continuation
                if line.endswith("\\"):
                    lines.append(line[:-1])  # Remove backslash
                    current_prompt = continuation_prompt
                    continue
                else:
                    lines.append(line)
                    break

            except KeyboardInterrupt:
                if lines:
                    print("Multi-line input cancelled")
                    return ""
                else:
                    raise

        return "\n".join(lines)

    def save_history(self):
        """Save command history to file."""
        try:
            # Create directory if it doesn't exist
            history_dir = os.path.dirname(self.history_file)
            if history_dir:
                os.makedirs(history_dir, exist_ok=True)

            # Save history
            self.readline.write_history_file(self.history_file)

        except PermissionError:
            print(f"Warning: Cannot save history to {self.history_file}")
        except Exception as e:
            print(f"Warning: Error saving history: {e}")

    def clear_history(self):
        """Clear command history."""
        self.readline.clear_history()

    def get_history_length(self) -> int:
        """Get current history length."""
        return self.readline.get_current_history_length()

    def get_history_item(self, index: int) -> Optional[str]:
        """
        Get history item at index.

        Args:
            index: History index (1-based)

        Returns:
            History item or None if index is invalid
        """
        try:
            return self.readline.get_history_item(index)
        except IndexError:
            return None

    def get_all_history(self) -> List[str]:
        """Get all history items."""
        history = []
        length = self.get_history_length()

        for i in range(1, length + 1):
            item = self.get_history_item(i)
            if item:
                history.append(item)

        return history

    def cleanup(self):
        """Clean up readline and save history."""
        self.save_history()

        # Reset readline state
        self.readline.set_completer(None)
        self.readline.clear_history()


def create_command_completer(commands: List[str]) -> Callable:
    """
    Create a tab completion function for commands.

    Args:
        commands: List of available commands

    Returns:
        Completer function for readline
    """

    def completer(text: str, state: int) -> Optional[str]:
        """Tab completion function."""
        # Import readline here to avoid circular imports
        import readline

        # Get current line buffer
        line_buffer = readline.get_line_buffer()

        # If we're at the beginning of the line, complete commands
        if line_buffer.lstrip() == text:
            matches = [cmd for cmd in commands if cmd.startswith(text)]
        else:
            # For other positions, try file path completion
            matches = []
            try:
                import glob

                pattern = text + "*"
                matches = glob.glob(pattern)
            except Exception:
                matches = []

        try:
            return matches[state]
        except IndexError:
            return None

    return completer
