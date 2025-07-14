"""
Main entry point for Claude Code Readline Client (CCRC).
"""

import asyncio
import sys

from .claude_client import ClaudeCodeClient


class CCRCApp:
    """Main application class for CCRC."""

    def __init__(self):
        self.client = ClaudeCodeClient()
        self.running = True

    async def run(self):
        """Main application loop."""
        print("Claude Code Readline Client (CCRC) v0.1.0")
        print("Type 'exit' or press Ctrl+C to quit")
        print("=" * 50)

        while self.running:
            try:
                # Get user input (will be replaced with readline later)
                prompt = input("\n> ")

                if prompt.lower() in ["exit", "quit"]:
                    break

                if not prompt.strip():
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

            except Exception as e:
                print(f"\nUnexpected error: {e}")
                print("Continuing...")

        self.running = False

    def stop(self):
        """Stop the application."""
        self.running = False


def main():
    """Main entry point."""
    app = CCRCApp()

    try:
        # Run the async application
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
