"""
Todo Assistant AI Agent

Main agent implementation using OpenAI Agents SDK for conversational
todo management.

Spec Reference: specs/agents/todo-agent.md
Tasks: 3.1-3.15
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import random

from openai import AsyncOpenAI
from app.agents.prompts import (
    get_system_prompt,
    get_context_prompt,
    RESPONSE_TEMPLATES,
    ENCOURAGEMENT_MESSAGES
)

logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Agent configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gpt-4-turbo")
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "500"))


async def process_chat_message(
    user_id: int,
    session_id: str,
    message: str,
    history: List[Dict],
    user_email: str = "",
    pending_count: int = 0,
    completed_count: int = 0
) -> Dict:
    """
    Process user chat message through AI agent

    Args:
        user_id: Authenticated user ID
        session_id: Chat session ID
        message: User's message
        history: Recent chat history
        user_email: User's email (optional)
        pending_count: Number of pending tasks (optional)
        completed_count: Number of completed tasks (optional)

    Returns:
        Dict with 'content' (response text) and 'metadata' (tool calls, etc.)

    Spec Reference: specs/agents/todo-agent.md - Agent Main Processing
    Task: 3.11
    """
    try:
        # Build system prompt
        system_prompt = get_system_prompt()

        # Build context prompt
        context_prompt = get_context_prompt(
            user_id=user_id,
            user_email=user_email,
            pending_count=pending_count,
            completed_count=completed_count,
            chat_history=history
        )

        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_prompt}
        ]

        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })

        # Define available tools (MCP tools as OpenAI functions)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "Create a new todo item for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "integer",
                                "description": "ID of the authenticated user"
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the todo (required)"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Priority level (optional)"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in ISO 8601 format (optional)"
                            }
                        },
                        "required": ["user_id", "title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_todos",
                    "description": "Retrieve user's todos with optional filters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed", "all"],
                                "description": "Filter by status"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Filter by priority"
                            },
                            "due_date_range": {
                                "type": "string",
                                "enum": ["today", "tomorrow", "this_week", "next_week", "overdue"],
                                "description": "Filter by relative date range"
                            }
                        },
                        "required": ["user_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Update an existing todo item",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer"},
                            "todo_id": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed"]
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"]
                            },
                            "due_date": {"type": "string"}
                        },
                        "required": ["user_id", "todo_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Delete a todo item (requires confirmation)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer"},
                            "todo_id": {"type": "integer"},
                            "confirm": {
                                "type": "boolean",
                                "description": "Must be true to confirm deletion"
                            }
                        },
                        "required": ["user_id", "todo_id", "confirm"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_todos",
                    "description": "Search todos by keyword in title and description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "integer"},
                            "query": {
                                "type": "string",
                                "description": "Search keyword or phrase"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed", "all"]
                            }
                        },
                        "required": ["user_id", "query"]
                    }
                }
            }
        ]

        # Log request
        logger.info(f"Processing message for user {user_id}: {message[:50]}...")

        # Call OpenAI with function calling
        response = await openai_client.chat.completions.create(
            model=AGENT_MODEL,
            messages=messages,
            tools=tools,
            temperature=AGENT_TEMPERATURE,
            max_tokens=AGENT_MAX_TOKENS
        )

        # Extract response
        assistant_message = response.choices[0].message

        # Check if tool calls were made
        tool_calls_made = []
        if assistant_message.tool_calls:
            # Import MCP tools
            from mcp_server.tools import (
                create_todo,
                list_todos,
                update_todo,
                delete_todo,
                search_todos
            )

            tool_map = {
                "create_todo": create_todo,
                "list_todos": list_todos,
                "update_todo": update_todo,
                "delete_todo": delete_todo,
                "search_todos": search_todos
            }

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = eval(tool_call.function.arguments)  # Parse JSON args

                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                if tool_name in tool_map:
                    tool_result = await tool_map[tool_name](**tool_args)
                    tool_calls_made.append({
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    })

        # Get final response content
        response_content = assistant_message.content or "I've processed your request."

        # Log response
        logger.info(f"Generated response for user {user_id}: {response_content[:50]}...")

        return {
            "content": response_content,
            "metadata": {
                "tool_calls": tool_calls_made,
                "model": AGENT_MODEL,
                "tokens_used": response.usage.total_tokens if response.usage else 0
            }
        }

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        return {
            "content": "I'm sorry, I encountered an error while processing your message. Please try again.",
            "metadata": {
                "error": str(e),
                "tool_calls": []
            }
        }
