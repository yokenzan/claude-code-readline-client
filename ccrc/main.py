"""
Main entry point for Claude Code Readline Client (CCRC).
"""

import asyncio
import sys
import atexit

from .claude_client import ClaudeCodeClient
from .input.readline_handler import (
    ReadlineInputHandler,
    create_command_completer,
)


class CCRCApp:
    """Main application class for CCRC."""

    def __init__(self, prefer_gnureadline: bool = False):
        self.client = ClaudeCodeClient()
        self.readline_handler = ReadlineInputHandler(prefer_gnureadline=prefer_gnureadline)
        self.running = True

        # Set up command completion
        commands = ["/help", "/clear", "/exit", "/history", "/save", "/load"]
        completer = create_command_completer(commands)
        self.readline_handler.set_completer(completer)

        # Register cleanup function
        atexit.register(self.cleanup)

    async def run(self):
        """Main application loop."""
        print("Claude Code Readline Client (CCRC) v0.1.0")
        print("Type 'exit' or press Ctrl+C to quit")
        print("=" * 50)

        while self.running:
            try:
                # Get user input with readline support
                prompt = self.readline_handler.get_input("\n> ")

                if prompt.lower() in ["exit", "quit", "/exit"]:
                    break

                if not prompt.strip():
                    continue

                # Handle special commands
                if prompt.startswith("/"):
                    self._handle_command(prompt)
                    continue

                # Send message to Claude and handle responses
                print("\nClaude:", end=" ")

                response_text = ""
                async for response in self.client.send_message(prompt):
                    if response.error:
                        print(f"\nError: {response.error}")
                        break

                    if response.text:
                        print(response.text, end="", flush=True)
                        response_text += response.text

                    if response.is_complete:
                        if response.cost_usd > 0:
                            print(f"\n[Cost: ${response.cost_usd:.4f}]")
                        else:
                            print()  # New line after response
                        break

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

            except Exception as e:
                print(f"\nUnexpected error: {e}")
                print("Continuing...")

        self.running = False

    def _handle_command(self, command: str):
        """Handle special commands."""
        cmd = command.strip().lower()

        if cmd == "/help":
            print("\nAvailable commands:")
            print("  /help     - Show this help message")
            print("  /clear    - Clear the screen")
            print("  /exit     - Exit the application")
            print("  /history  - Show command history")
            print("  /save     - Save current session (not implemented)")
            print("  /load     - Load saved session (not implemented)")
            print("\nKeyboard shortcuts:")
            print("  Uses GNU Readline defaults - see 'man readline' for details")
            print("  Configuration: ~/.inputrc file is loaded if present")
            print(
                "  Common shortcuts: Ctrl+A (start), Ctrl+E (end), Ctrl+K (kill line)"
            )
            print("  Ctrl+R (search history), Ctrl+C (cancel), Ctrl+D (exit)")

        elif cmd == "/clear":
            import os

            os.system("clear" if os.name == "posix" else "cls")

        elif cmd == "/exit":
            self.running = False

        elif cmd == "/history":
            history = self.readline_handler.get_all_history()
            if history:
                print("\nCommand history:")
                for i, item in enumerate(history[-20:], 1):  # Show last 20
                    print(f"  {i:2d}: {item}")
            else:
                print("\nNo history available.")

        elif cmd == "/save":
            print("Session save functionality not implemented yet.")

        elif cmd == "/load":
            print("Session load functionality not implemented yet.")

        else:
            print(f"Unknown command: {command}")
            print("Type /help for available commands.")

    def stop(self):
        """Stop the application."""
        self.running = False

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, "readline_handler"):
            self.readline_handler.cleanup()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code Readline Client")
    parser.add_argument(
        "--gnureadline", 
        action="store_true", 
        help="Prefer gnureadline over standard readline library"
    )
    
    args = parser.parse_args()
    app = CCRCApp(prefer_gnureadline=args.gnureadline)

    try:
        # Run the async application
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
