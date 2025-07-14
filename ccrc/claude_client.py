"""
Claude Code SDK client for CCRC.
"""

import asyncio
from typing import AsyncGenerator, Optional, List
from dataclasses import dataclass
from pathlib import Path

try:
    from claude_code_sdk import (
        query,
        ClaudeCodeOptions,
        AssistantMessage,
        ResultMessage,
        TextBlock,
        ClaudeSDKError,
        CLINotFoundError,
        CLIConnectionError,
        ProcessError,
        CLIJSONDecodeError,
    )
except ImportError:
    # Fallback for development/testing
    print("Warning: claude_code_sdk not available, using mock implementation")
    from unittest.mock import AsyncMock
    
    class MockMessage:
        pass
    
    class AssistantMessage(MockMessage):
        def __init__(self, content):
            self.content = content
    
    class TextBlock:
        def __init__(self, text):
            self.text = text
    
    class ResultMessage(MockMessage):
        def __init__(self, total_cost_usd=0.0):
            self.total_cost_usd = total_cost_usd
    
    class ClaudeSDKError(Exception):
        pass
    
    class CLINotFoundError(ClaudeSDKError):
        pass
    
    class CLIConnectionError(ClaudeSDKError):
        pass
    
    class ProcessError(ClaudeSDKError):
        def __init__(self, exit_code):
            self.exit_code = exit_code
    
    class CLIJSONDecodeError(ClaudeSDKError):
        pass
    
    class ClaudeCodeOptions:
        def __init__(self, system_prompt=None, max_turns=None, cwd=None, 
                     allowed_tools=None, permission_mode=None):
            self.system_prompt = system_prompt
            self.max_turns = max_turns
            self.cwd = cwd
            self.allowed_tools = allowed_tools
            self.permission_mode = permission_mode
    
    async def query(prompt: str, options: Optional[ClaudeCodeOptions] = None):
        # Mock implementation for testing
        yield AssistantMessage([TextBlock(f"Mock response to: {prompt}")])
        yield ResultMessage(0.001)


@dataclass
class ClaudeResponse:
    """Represents a response from Claude Code."""
    text: str
    is_complete: bool
    cost_usd: float = 0.0
    error: Optional[str] = None


class ClaudeCodeClient:
    """Client for interacting with Claude Code SDK."""
    
    def __init__(self, 
                 system_prompt: Optional[str] = None,
                 max_turns: int = 10,
                 cwd: Optional[Path] = None,
                 allowed_tools: Optional[List[str]] = None,
                 permission_mode: str = "acceptEdits"):
        """
        Initialize Claude Code client.
        
        Args:
            system_prompt: Custom system prompt
            max_turns: Maximum conversation turns
            cwd: Working directory
            allowed_tools: List of allowed tools
            permission_mode: Permission handling mode
        """
        self.options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            max_turns=max_turns,
            cwd=str(cwd) if cwd else None,
            allowed_tools=allowed_tools or ["Read", "Write", "Bash", "Edit"],
            permission_mode=permission_mode
        )
        self._conversation_active = False
    
    async def send_message(self, prompt: str) -> AsyncGenerator[ClaudeResponse, None]:
        """
        Send a message to Claude Code and yield responses.
        
        Args:
            prompt: User's prompt/message
            
        Yields:
            ClaudeResponse: Streaming responses from Claude
        """
        try:
            self._conversation_active = True
            
            async for message in query(prompt=prompt, options=self.options):
                if isinstance(message, AssistantMessage):
                    # Extract text from assistant message
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            yield ClaudeResponse(
                                text=block.text,
                                is_complete=False
                            )
                
                elif isinstance(message, ResultMessage):
                    # Final message with cost information
                    yield ClaudeResponse(
                        text="",
                        is_complete=True,
                        cost_usd=message.total_cost_usd
                    )
        
        except CLINotFoundError:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error="Claude Code CLI not found. Please install it first."
            )
        
        except CLIConnectionError:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error="Connection error. Check your network connection and authentication."
            )
        
        except ProcessError as e:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error=f"Process failed with exit code: {e.exit_code}"
            )
        
        except CLIJSONDecodeError as e:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error=f"Failed to parse JSON response: {e}"
            )
        
        except ClaudeSDKError as e:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error=f"SDK error: {e}"
            )
        
        except Exception as e:
            yield ClaudeResponse(
                text="",
                is_complete=True,
                error=f"Unexpected error: {e}"
            )
        
        finally:
            self._conversation_active = False
    
    @property
    def is_active(self) -> bool:
        """Check if conversation is currently active."""
        return self._conversation_active
    
    def update_options(self, **kwargs):
        """Update client options."""
        for key, value in kwargs.items():
            if hasattr(self.options, key):
                setattr(self.options, key, value)