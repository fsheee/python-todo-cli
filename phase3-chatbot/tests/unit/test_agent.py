"""
Unit tests for the Todo Assistant Agent.

Spec Reference: specs/agents/todo-agent.md - Testing Strategy
Task: 3.15
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.agents.todo_agent import process_chat_message
from app.agents.prompts import get_system_prompt, get_context_prompt

@pytest.mark.asyncio
async def test_process_chat_message_success(sample_chat_messages):
    """Test successful processing of a chat message with intent recognition."""
    user_id = "123"
    session_id = "sess_123"
    message = "Add buy milk"

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()

    # Simulate a tool call response
    mock_message.content = None
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_abc123"
    mock_tool_call.function.name = "create_todo"
    mock_tool_call.function.arguments = json.dumps({
        "user_id": user_id,
        "title": "Buy milk"
    })
    mock_message.tool_calls = [mock_tool_call]
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 100

    # Mock tool execution
    mock_tool_result = {"success": True, "todo_id": 456, "title": "Buy milk"}

    # Mock final response after tool execution
    mock_final_response = MagicMock()
    mock_final_choice = MagicMock()
    mock_final_message = MagicMock()
    mock_final_message.content = "I've added 'Buy milk' to your list."
    mock_final_choice.message = mock_final_message
    mock_final_response.choices = [mock_final_choice]
    mock_final_response.usage.total_tokens = 50

    with patch("app.agents.todo_agent.openai_client.chat.completions.create", new_callable=AsyncMock, side_effect=[mock_response, mock_final_response]) as mock_create, \
         patch("mcp_server.tools.create_todo", new_callable=AsyncMock) as mock_create_todo:

        mock_create_todo.return_value = mock_tool_result

        result = await process_chat_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            history=[],
            jwt_token="fake_token"
        )

        # Verify
        assert result["content"] == "I've added 'Buy milk' to your list."
        assert len(result["metadata"]["tool_calls"]) == 1
        assert result["metadata"]["tool_calls"][0]["tool"] == "create_todo"
        assert result["metadata"]["tool_calls"][0]["result"] == mock_tool_result

        # Verify calls
        assert mock_create.call_count == 2
        mock_create_todo.assert_called_once()

@pytest.mark.asyncio
async def test_process_chat_message_conversational():
    """Test processing of a simple conversational message (no tool call)."""
    user_id = "123"
    session_id = "sess_123"
    message = "Hello"

    # Mock OpenAI response (direct response)
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Hello! How can I help you today?"
    mock_message.tool_calls = None
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 50

    with patch("app.agents.todo_agent.openai_client.chat.completions.create", new_callable=AsyncMock, return_value=mock_response) as mock_create:
        result = await process_chat_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            history=[],
            jwt_token="fake_token"
        )

        assert result["content"] == "Hello! How can I help you today?"
        assert len(result["metadata"]["tool_calls"]) == 0

        # Verify calls
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_process_chat_message_error_handling():
    """Test error handling during processing."""
    user_id = "123"
    session_id = "sess_123"
    message = "Add buy milk"

    with patch("app.agents.todo_agent.openai_client.chat.completions.create", new_callable=AsyncMock, side_effect=Exception("API Error")):
        result = await process_chat_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            history=[],
            jwt_token="fake_token"
        )

        assert "I'm sorry, I encountered an error" in result["content"]
        assert result["metadata"]["error"] == "API Error"

def test_system_prompt_generation():
    """Test system prompt generation."""
    prompt = get_system_prompt(current_date="2025-12-25")
    assert "2025-12-25" in prompt
    assert "You are a helpful AI assistant" in prompt
    assert "Available MCP Tools" not in prompt  # Context prompt has tools

def test_context_prompt_generation():
    """Test context prompt generation."""
    history = [{"role": "user", "content": "Hi"}]
    prompt = get_context_prompt(
        user_id=123,
        user_email="test@example.com",
        pending_count=5,
        completed_count=2,
        chat_history=history
    )

    assert "User ID: 123" in prompt
    assert "Email: test@example.com" in prompt
    assert "Current tasks count: 5 pending, 2 completed" in prompt
    assert "user: Hi" in prompt
