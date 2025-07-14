"""
Tests for Claude Code client.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from ccrc.claude_client import ClaudeCodeClient, ClaudeResponse


class TestClaudeCodeClient:
    """Test suite for ClaudeCodeClient."""

    def test_init(self):
        """Test client initialization."""
        client = ClaudeCodeClient()
        assert client.options.max_turns == 10
        assert client.options.permission_mode == "acceptEdits"
        assert "Read" in client.options.allowed_tools
        assert not client.is_active

    def test_init_with_options(self):
        """Test client initialization with custom options."""
        client = ClaudeCodeClient(
            system_prompt="Custom prompt",
            max_turns=5,
            cwd=Path("/tmp"),
            allowed_tools=["Read", "Write"],
            permission_mode="ask",
        )
        assert client.options.system_prompt == "Custom prompt"
        assert client.options.max_turns == 5
        assert client.options.cwd == "/tmp"
        assert client.options.allowed_tools == ["Read", "Write"]
        assert client.options.permission_mode == "ask"

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        """Test successful message sending."""
        # Mock the query function to return test responses
        mock_text_block = MagicMock()
        mock_text_block.text = "Hello, how can I help you?"

        async def mock_query(prompt, options):
            from ccrc.claude_client import (
                AssistantMessage,
                ResultMessage,
                TextBlock,
            )

            yield AssistantMessage([TextBlock("Hello, how can I help you?")])
            yield ResultMessage(0.001)

        with patch("ccrc.claude_client.query", mock_query):
            client = ClaudeCodeClient()

            responses = []
            async for response in client.send_message("Hello"):
                responses.append(response)

            # Should get text response and completion response
            assert len(responses) == 2
            assert responses[0].text == "Hello, how can I help you?"
            assert not responses[0].is_complete
            assert responses[1].is_complete
            assert responses[1].cost_usd == 0.001

    @pytest.mark.asyncio
    async def test_send_message_cli_not_found(self):
        """Test handling of CLI not found error."""
        from ccrc.claude_client import CLINotFoundError

        async def mock_query(prompt, options):
            raise CLINotFoundError()
            # This yield is never reached but needed to make it a generator
            yield  # pragma: no cover

        with patch("ccrc.claude_client.query", mock_query):
            client = ClaudeCodeClient()

            responses = []
            async for response in client.send_message("Hello"):
                responses.append(response)

            assert len(responses) == 1
            assert responses[0].is_complete
            assert "Claude Code CLI not found" in responses[0].error

    @pytest.mark.asyncio
    async def test_send_message_connection_error(self):
        """Test handling of connection error."""
        from ccrc.claude_client import CLIConnectionError

        async def mock_query(prompt, options):
            raise CLIConnectionError()
            # This yield is never reached but needed to make it a generator
            yield  # pragma: no cover

        with patch("ccrc.claude_client.query", mock_query):
            client = ClaudeCodeClient()

            responses = []
            async for response in client.send_message("Hello"):
                responses.append(response)

            assert len(responses) == 1
            assert responses[0].is_complete
            assert "Connection error" in responses[0].error

    def test_update_options(self):
        """Test updating client options."""
        client = ClaudeCodeClient()

        client.update_options(max_turns=20, system_prompt="New prompt")

        assert client.options.max_turns == 20
        assert client.options.system_prompt == "New prompt"

    def test_is_active_property(self):
        """Test is_active property."""
        client = ClaudeCodeClient()
        assert not client.is_active

        # This would be set during actual message sending
        client._conversation_active = True
        assert client.is_active


class TestClaudeResponse:
    """Test suite for ClaudeResponse."""

    def test_claude_response_creation(self):
        """Test creating ClaudeResponse objects."""
        response = ClaudeResponse(
            text="Hello", is_complete=False, cost_usd=0.001
        )

        assert response.text == "Hello"
        assert not response.is_complete
        assert response.cost_usd == 0.001
        assert response.error is None

    def test_claude_response_with_error(self):
        """Test creating ClaudeResponse with error."""
        response = ClaudeResponse(
            text="", is_complete=True, error="Test error"
        )

        assert response.text == ""
        assert response.is_complete
        assert response.error == "Test error"
        assert response.cost_usd == 0.0
