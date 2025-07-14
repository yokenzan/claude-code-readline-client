"""
Tests for Readline input handler.
"""

import os
import pytest
import unittest.mock
from unittest.mock import patch

from ccrc.input.readline_handler import (
    ReadlineInputHandler,
    create_command_completer,
)


class TestReadlineInputHandler:
    """Test suite for ReadlineInputHandler."""

    def test_init_default(self):
        """Test default initialization."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import:
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline

            handler = ReadlineInputHandler()

            assert handler.history_size == 10000
            assert handler.history_file == os.path.expanduser("~/.ccrc_history")
            assert handler.completer_function is None
            assert handler.prefer_gnureadline is False
            mock_import.assert_called_once_with(False, False)

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import:
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline

            handler = ReadlineInputHandler(
                history_file="/tmp/test_history",
                history_size=5000,
                prefer_gnureadline=True,
            )

            assert handler.history_size == 5000
            assert handler.history_file == "/tmp/test_history"
            assert handler.prefer_gnureadline is True
            mock_import.assert_called_once_with(True, False)

    def test_init_with_rl(self):
        """Test initialization with rl library preference."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import:
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline

            handler = ReadlineInputHandler(
                history_file="/tmp/test_history",
                history_size=5000,
                prefer_rl=True,
            )

            assert handler.history_size == 5000
            assert handler.history_file == "/tmp/test_history"
            assert handler.prefer_rl is True
            mock_import.assert_called_once_with(False, True)

    def test_setup_readline_calls(self):
        """Test that readline setup methods are called."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import, patch("os.path.exists", return_value=True):
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline

            ReadlineInputHandler()

            mock_readline.set_history_length.assert_called_once_with(10000)
            mock_readline.read_history_file.assert_called_once()
            mock_readline.set_completer_delims.assert_called_once()
            mock_readline.read_init_file.assert_called_once()
            # Should have parse_and_bind calls for tab completion and potentially advanced commands
            assert mock_readline.parse_and_bind.call_count >= 1

    def test_history_file_not_exists(self):
        """Test behavior when history file doesn't exist."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ) as mock_read_history, patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ):

            ReadlineInputHandler()

            mock_read_history.assert_not_called()

    def test_history_file_permission_error(self):
        """Test handling of permission error when reading history."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import:
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline
            mock_readline.read_history_file.side_effect = PermissionError

            with patch("os.path.exists", return_value=True), patch(
                "builtins.print"
            ) as mock_print:

                handler = ReadlineInputHandler()

                # Check that the warning was printed (should be one of the calls)
                expected_call = unittest.mock.call(
                    f"Warning: Cannot read history file {handler.history_file}"
                )
                assert expected_call in mock_print.call_args_list

    def test_set_completer(self):
        """Test setting custom completer function."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "readline.set_completer"
        ) as mock_set_completer, patch(
            "os.path.exists", return_value=False
        ):

            handler = ReadlineInputHandler()

            def test_completer(text, state):
                return f"completion_{state}"

            handler.set_completer(test_completer)

            assert handler.completer_function == test_completer
            mock_set_completer.assert_called_once_with(test_completer)

    def test_get_input_success(self):
        """Test successful input retrieval."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "builtins.input", return_value="test input"
        ), patch(
            "readline.add_history"
        ) as mock_add_history:

            handler = ReadlineInputHandler()
            result = handler.get_input("> ")

            assert result == "test input"
            mock_add_history.assert_called_once_with("test input")

    def test_get_input_empty(self):
        """Test input retrieval with empty string."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "builtins.input", return_value="   "
        ), patch(
            "readline.add_history"
        ) as mock_add_history:

            handler = ReadlineInputHandler()
            result = handler.get_input("> ")

            assert result == "   "
            mock_add_history.assert_not_called()

    def test_get_input_keyboard_interrupt(self):
        """Test handling of KeyboardInterrupt."""
        with patch(
            "ccrc.input.readline_handler._import_readline_library"
        ) as mock_import:
            mock_readline = unittest.mock.MagicMock()
            mock_import.return_value = mock_readline

            with patch("os.path.exists", return_value=False), patch(
                "builtins.input", side_effect=KeyboardInterrupt
            ), patch("builtins.print") as mock_print:

                handler = ReadlineInputHandler()

                with pytest.raises(KeyboardInterrupt):
                    handler.get_input("> ")

                # Check that the newline print was called (should be one of the calls)
                expected_call = unittest.mock.call()
                assert expected_call in mock_print.call_args_list

    def test_get_multiline_input_no_continuation(self):
        """Test multi-line input without continuation."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "builtins.input", return_value="single line"
        ), patch(
            "readline.add_history"
        ):

            handler = ReadlineInputHandler()
            result = handler.get_multiline_input("> ", "... ")

            assert result == "single line"

    def test_get_multiline_input_with_continuation(self):
        """Test multi-line input with backslash continuation."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "builtins.input", side_effect=["first line \\", "second line"]
        ), patch(
            "readline.add_history"
        ):

            handler = ReadlineInputHandler()
            result = handler.get_multiline_input("> ", "... ")

            assert result == "first line \nsecond line"

    def test_save_history(self):
        """Test saving history to file."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.write_history_file"
        ) as mock_write_history, patch(
            "os.makedirs"
        ) as mock_makedirs:

            handler = ReadlineInputHandler(history_file="/tmp/test/history")
            handler.save_history()

            mock_makedirs.assert_called_once_with("/tmp/test", exist_ok=True)
            mock_write_history.assert_called_once_with("/tmp/test/history")

    def test_save_history_permission_error(self):
        """Test handling of permission error when saving history."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.write_history_file", side_effect=PermissionError
        ), patch(
            "os.makedirs"
        ), patch(
            "builtins.print"
        ) as mock_print:

            handler = ReadlineInputHandler()
            handler.save_history()

            mock_print.assert_called_with(
                f"Warning: Cannot save history to {handler.history_file}"
            )

    def test_get_history_length(self):
        """Test getting history length."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.get_current_history_length", return_value=5
        ):

            handler = ReadlineInputHandler()
            assert handler.get_history_length() == 5

    def test_get_history_item(self):
        """Test getting history item."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.get_history_item", return_value="test item"
        ):

            handler = ReadlineInputHandler()
            assert handler.get_history_item(1) == "test item"

    def test_get_history_item_index_error(self):
        """Test getting history item with invalid index."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.get_history_item", side_effect=IndexError
        ):

            handler = ReadlineInputHandler()
            assert handler.get_history_item(999) is None

    def test_cleanup(self):
        """Test cleanup method."""
        with patch("readline.set_history_length"), patch(
            "readline.read_history_file"
        ), patch("readline.parse_and_bind"), patch(
            "readline.set_completer_delims"
        ), patch(
            "os.path.exists", return_value=False
        ), patch(
            "readline.write_history_file"
        ) as mock_write_history, patch(
            "readline.set_completer"
        ) as mock_set_completer, patch(
            "readline.clear_history"
        ) as mock_clear_history, patch(
            "os.makedirs"
        ):

            handler = ReadlineInputHandler()
            handler.cleanup()

            mock_write_history.assert_called_once()
            mock_set_completer.assert_called_once_with(None)
            mock_clear_history.assert_called_once()


class TestImportReadlineLibrary:
    """Test the _import_readline_library function."""

    def test_rl_library_precedence(self):
        """Test that rl library takes precedence when prefer_rl=True."""
        with patch("builtins.print") as mock_print:
            # Test that the function works with actual rl library if available
            from ccrc.input.readline_handler import _import_readline_library

            # This should import the rl library since it's installed
            result = _import_readline_library(prefer_rl=True)

            # Verify that the rl library was selected
            assert hasattr(result, "parse_and_bind")
            mock_print.assert_called_with("Using rl library")

    def test_library_fallback(self):
        """Test library fallback behavior."""
        # Test the actual library selection logic
        from ccrc.input.readline_handler import _import_readline_library

        with patch("builtins.print") as mock_print:
            # Without any preferences, should use standard readline
            result = _import_readline_library(prefer_rl=False, prefer_gnureadline=False)

            # Should have readline functionality
            assert hasattr(result, "parse_and_bind")

            # Should indicate which library was used
            assert mock_print.called
            print_args = mock_print.call_args[0][0]
            assert "Using" in print_args and "library" in print_args


class TestCreateCommandCompleter:
    """Test suite for create_command_completer function."""

    def test_command_completion_at_start(self):
        """Test command completion at line start."""
        commands = ["/help", "/clear", "/exit"]
        completer = create_command_completer(commands)

        with patch("readline.get_line_buffer", return_value="/h"):
            assert completer("/h", 0) == "/help"
            assert completer("/h", 1) is None

    def test_command_completion_multiple_matches(self):
        """Test command completion with multiple matches."""
        commands = ["/help", "/history", "/halt"]
        completer = create_command_completer(commands)

        with patch("readline.get_line_buffer", return_value="/h"):
            matches = []
            for i in range(10):  # Try to get all matches
                match = completer("/h", i)
                if match is None:
                    break
                matches.append(match)

            assert "/help" in matches
            assert "/history" in matches
            assert "/halt" in matches

    def test_file_completion_not_at_start(self):
        """Test file completion when not at line start."""
        commands = ["/help", "/clear"]
        completer = create_command_completer(commands)

        with patch("readline.get_line_buffer", return_value="command /tm"), patch(
            "glob.glob", return_value=["/tmp/file1", "/tmp/file2"]
        ):

            assert completer("/tm", 0) == "/tmp/file1"
            assert completer("/tm", 1) == "/tmp/file2"
            assert completer("/tm", 2) is None
