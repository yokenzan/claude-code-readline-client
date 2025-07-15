"""
GNU Readline input handler for CCRC.
"""

import os
from enum import Enum
from typing import Optional, List, Callable, Any


class ReadlineLibrary(Enum):
    """Enum for available readline library options."""

    AUTO = "auto"
    READLINE = "readline"
    GNUREADLINE = "gnureadline"
    RL = "rl"


def _import_readline_library(library: ReadlineLibrary = ReadlineLibrary.AUTO) -> Any:
    """
    Import readline library based on the specified preference.

    Args:
        library: Which readline library to use

    Returns:
        Imported readline module
    """
    readline_lib = None
    library_name = "unknown"

    if library == ReadlineLibrary.AUTO:
        # Try libraries in order of feature richness: rl > gnureadline > readline
        for lib_choice in [
            ReadlineLibrary.RL,
            ReadlineLibrary.GNUREADLINE,
            ReadlineLibrary.READLINE,
        ]:
            try:
                readline_lib, library_name = _try_import_single_library(lib_choice)
                break
            except ImportError:
                continue
    else:
        # Try the specific library requested
        readline_lib, library_name = _try_import_single_library(library)

    if readline_lib is None:
        raise ImportError(
            "No readline library available. Install readline, gnureadline, or rl."
        )

    print(f"Using {library_name} library")
    return readline_lib


def _try_import_single_library(library: ReadlineLibrary) -> tuple[Any, str]:
    """
    Try to import a specific readline library.

    Args:
        library: The specific library to import

    Returns:
        Tuple of (imported_module, library_name)

    Raises:
        ImportError: If the library cannot be imported
    """
    if library == ReadlineLibrary.RL:
        import rl.readline as readline_lib

        return readline_lib, "rl"
    elif library == ReadlineLibrary.GNUREADLINE:
        import gnureadline as readline_lib

        return readline_lib, "gnureadline"
    elif library == ReadlineLibrary.READLINE:
        import readline as readline_lib

        return readline_lib, "readline"
    else:
        raise ImportError(f"Unknown library: {library}")


class ReadlineInputHandler:
    """Handles GNU Readline input with history and key bindings."""

    def __init__(
        self,
        history_file: Optional[str] = None,
        history_size: int = 10000,
        library: ReadlineLibrary = ReadlineLibrary.AUTO,
    ):
        """
        Initialize readline input handler.

        Args:
            history_file: Path to history file (default: ~/.ccrc_history)
            history_size: Maximum number of history entries
            library: Which readline library to use
        """
        self.history_file = history_file or os.path.expanduser("~/.ccrc_history")
        self.history_size = history_size
        self.completer_function: Optional[Callable] = None
        self.library = library

        # Import readline library
        self.readline = _import_readline_library(library)

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
