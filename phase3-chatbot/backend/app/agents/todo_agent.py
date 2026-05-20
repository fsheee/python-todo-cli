"""
Todo Assistant AI Agent

Main agent implementation using OpenAI Agents SDK for conversational
todo management.

Spec Reference: specs/agents/todo-agent.md
Tasks: 3.1-3.15
"""

import os
import json
import logging
import asyncio
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

# Initialize AI client prioritizing OpenRouter
# We use the AsyncOpenAI client because OpenRouter provides an OpenAI-compatible API
OPEN_ROUTER_API_KEY = (
    os.getenv("OPEN_ROUTER_API_KEY")
    or os.getenv("OPENROUTER_API_KEY")
    # Legacy typo support
    or os.getenv("OPEN_ROTER_API_KEY")
)
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "fake_key_for_tests")

if OPEN_ROUTER_API_KEY:
    # Primary: Use OpenRouter
    openai_client = AsyncOpenAI(
        api_key=OPEN_ROUTER_API_KEY,
        base_url=BASE_URL
    )
    logger.info(f"Using OpenRouter API for AI requests (URL: {BASE_URL})")
else:
    # Fallback: Use direct OpenAI
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    logger.info("Using OpenAI API for AI requests (Direct)")

# Agent configuration
# Default to a free model on OpenRouter if not specified
AGENT_MODEL = os.getenv("AGENT_MODEL") or os.getenv("model_name") or "google/gemini-2.0-flash-001"
AGENT_TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "500"))


async def get_fallback_response(message: str, user_id: str, jwt_token: str = "") -> Dict:
    """Execute actual todo operations when AI API fails"""
    # Try to import MCP tools, but don't fail if they don't exist
    try:
        from mcp_server.tools.create_todo import create_todo
        from mcp_server.tools.list_todos import list_todos
        from mcp_server.tools.update_todo import update_todo
        from mcp_server.tools.delete_todo import delete_todo
        tools_available = True
    except Exception:
        tools_available = False

    message_lower = message.lower().strip()

    # Only try todo operations if tools are available
    if tools_available:
        try:
            # ADD TASK
            if any(k in message_lower for k in ["add", "create", "new", "make"]):
                if any(k in message_lower for k in ["task", "todo", "item"]):
                    words = message.split()
                    title = " ".join(words[1:]) if len(words) > 1 else "New task"
                    result = await create_todo(user_id=user_id, title=title, jwt_token=jwt_token)
                    return {
                        "content": f"✅ Task '{title}' added!",
                        "metadata": {"fallback": True, "operation": "create_todo", "result": result}
                    }
                words = message.split()
                title = " ".join(words[1:]) if len(words) > 1 else "New task"
                result = await create_todo(user_id=user_id, title=title, jwt_token=jwt_token)
                return {
                    "content": f"✅ Task '{title}' added!",
                    "metadata": {"fallback": True, "operation": "create_todo", "result": result}
                }
            # LIST TASKS
            elif any(k in message_lower for k in ["show", "list", "view", "display"]):
                result = await list_todos(user_id=user_id, status="all", jwt_token=jwt_token)
                tasks = result.get("todos", []) if isinstance(result, dict) else []
                if tasks:
                    task_list = "\n".join([f"{i+1}. {t.get('title','Untitled')} ({t.get('status','pending')})" for i,t in enumerate(tasks)])
                    return {
                        "content": f"📋 Your tasks:\n{task_list}",
                        "metadata": {"fallback": True, "operation": "list_todos", "count": len(tasks)}
                    }
                return {
                    "content": "📋 No tasks found!",
                    "metadata": {"fallback": True, "operation": "list_todos"}
                }
            # COMPLETE TASK
            elif any(k in message_lower for k in ["complete", "done", "finish", "mark"]):
                words = message.split()
                task_id = next((w for w in words if w.isdigit()), None)
                if not task_id:
                    return {
                        "content": (
                            "❌ Please specify the task ID to complete. "
                            "Use **show my tasks** to see the exact task ID."
                        ),
                        "metadata": {"fallback": True, "operation": "update_todo", "result": {"success": False, "error": "Missing task identifier", "code": "INVALID_TASK_ID"}},
                    }
                result = await update_todo(user_id=user_id, todo_id=task_id, status="completed", jwt_token=jwt_token)
                return {
                    "content": f"✅ Task {task_id} marked as complete!",
                    "metadata": {"fallback": True, "operation": "update_todo", "result": result}
                }
            # UPDATE TASK
            elif any(k in message_lower for k in ["update", "change", "modify", "edit", "set"]):
                words = message.split()
                task_id = next((w for w in words if w.isdigit() or ('-' in w and len(w) > 20)), None)
                if not task_id:
                    return {
                        "content": "I see you want to update a task. Please specify the task ID and what to change, e.g., **update <id> set priority high**.",
                        "metadata": {"fallback": True, "operation": "update_todo", "result": {"success": False, "error": "Missing task identifier", "code": "INVALID_TASK_ID"}},
                    }
                pass  # Let LLM handle field extraction
            # DELETE TASK
            elif any(k in message_lower for k in ["delete", "remove", "clear"]):
                words = message.split()
                task_id = next((w for w in words if w.isdigit()), None)
                if not task_id:
                    return {
                        "content": (
                            "❌ Please specify the task ID to delete. "
                            "Use **show my tasks** to see the exact task ID."
                        ),
                        "metadata": {"fallback": True, "operation": "delete_todo", "result": {"success": False, "error": "Missing task identifier", "code": "INVALID_TASK_ID"}},
                    }
                result = await delete_todo(user_id=user_id, todo_id=task_id, jwt_token=jwt_token)
                return {
                    "content": f"🗑️ Task {task_id} deleted!",
                    "metadata": {"fallback": True, "operation": "delete_todo", "result": result}
                }
        except Exception as e:
            # Don't fail - just continue to default response
            logger.error(f"Fallback tool error: {e}")

    # Default fallback when intent not recognized
    # Always return something useful - never fail!
    return {
        "content": "I understand your message! I'm your todo assistant. You can:\n📝 Add tasks: 'add buy milk'\n✅ Complete tasks: 'complete 1'\n📋 List tasks: 'show my tasks'\n✏️ Update tasks: 'update <id> set priority high'\n\nHow can I help you?",
        "metadata": {"fallback": True, "unrecognized": True}
    }


async def process_chat_message(
    user_id: str,
    session_id: str,
    message: str,
    history: List[Dict],
    jwt_token: str = "",
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
        tools: List[Dict] = [
            {
                "type": "function",
                "function": {
                    "name": "create_todo",
                    "description": "Create a new todo item for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
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
                        "required": ["title"]
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
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_todo",
                    "description": "Update an existing todo item. Use numeric reference (e.g., 1, 2) from the last list if todo_id is unknown.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "todo_id": {
                                "type": "string",
                                "description": "ID of the todo to update (can be UUID or numeric reference like '1')"
                            },
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
                        "required": ["todo_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_todo",
                    "description": "Delete a todo item (requires confirmation). Use numeric reference if todo_id is unknown. AGENT MUST CHECK HISTORY FOR CONFIRMATION.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "todo_id": {
                                "type": "string",
                                "description": "ID of the todo to delete (can be UUID or numeric reference like '1')"
                            },
                            "confirm": {
                                "type": "boolean",
                                "description": "Must be true to confirm deletion. Set to true ONLY if you see user explicitly confirming 'yes' or similar in recent history."
                            }
                        },
                        "required": ["todo_id", "confirm"]
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
                            "query": {
                                "type": "string",
                                "description": "Search keyword or phrase"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "completed", "all"]
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        # Log request
        logger.info(f"Processing message for user {user_id}: {message[:50]}...")

        # Call OpenAI with function calling
        response = None
        retry_count = 0
        max_retries = 1

        while retry_count < max_retries:
            try:
                response = await openai_client.chat.completions.create(
                    model=AGENT_MODEL,
                    messages=messages, # type: ignore
                    tools=tools, # type: ignore
                    temperature=AGENT_TEMPERATURE,
                    max_tokens=AGENT_MAX_TOKENS,
                    parallel_tool_calls=False  # Disable parallel tool calls for better compatibility
                )
                break  # Success, exit retry loop
            except Exception as e:
                error_str = str(e).lower()
                logger.error(f"API call failed: {str(e)}")

                # Check for rate limit errors
                if any(keyword in error_str for keyword in ["429", "rate limit", "rate-limit", "too many requests"]):
                    logger.error("Rate limit exceeded, using fallback response")
                    break

                # For other errors, retry once without tools
                if retry_count == 0:
                    logger.warning(f"Retrying API call without tools ({retry_count + 1}/{max_retries})...")
                    try:
                        response = await openai_client.chat.completions.create(
                            model=AGENT_MODEL,
                            messages=messages, # type: ignore
                            temperature=AGENT_TEMPERATURE,
                            max_tokens=AGENT_MAX_TOKENS
                        )
                        break  # Success, exit retry loop
                    except Exception as e2:
                        logger.error(f"Second attempt failed: {str(e2)}")

                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)  # Wait before retry

        if not response:
            # All attempts failed, use fallback response
            logger.warning("All API attempts failed, using fallback response")
            return await get_fallback_response(message, user_id, jwt_token=jwt_token)

        # Extract response
        assistant_message = response.choices[0].message

        # Check if tool calls were made
        tool_calls_made = []
        if assistant_message.tool_calls:
            # Prefer calling MCP tools directly.
            # The MCP SDK has dependency constraints (pydantic v2) that are
            # incompatible with this project’s FastAPI/sqlmodel pins.
            from mcp_server import tools as mcp_tools

            mcp_app = None
            CallToolRequest = None
            try:
                # Optional: if MCP SDK is available and compatible, use protocol layer
                from mcp_server.server import app as mcp_app  # type: ignore
                from mcp.types import CallToolRequest  # type: ignore
            except Exception:
                mcp_app = None
                CallToolRequest = None


            # Helper to resolve Numeric References to UUIDs
            def resolve_todo_id(ref: str) -> str:
                if not ref: return ref
                # If it looks like a number, try to find it in previous tool results
                if str(ref).isdigit():
                    idx = int(ref) - 1
                    for msg in reversed(history):
                        if "metadata" in msg and msg["metadata"] and "tool_calls" in msg["metadata"]:
                            for tc in msg["metadata"]["tool_calls"]:
                                if tc["tool"] in ["list_todos", "search_todos"]:
                                    trades = tc["result"]
                                    # res_data might be a content block, a list, or direct dict
                                    res_data = trades
                                    if isinstance(trades, list) and trades:
                                        res_data = trades[0]

                                    # Handle MCP TextContent objects or direct dicts
                                    # Use getattr for robustness
                                    if hasattr(res_data, "text"):
                                        try:
                                            res_data = json.loads(getattr(res_data, "text"))
                                        except:
                                            continue

                                    if not isinstance(res_data, dict):
                                        continue

                                    todos = res_data.get("todos", [])
                                    if 0 <= idx < len(todos):
                                        resolved = str(todos[idx].get("id"))
                                        logger.info(f"Resolved numeric reference {ref} to {resolved}")
                                        return resolved
                return str(ref)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                # Use getattr or check for function attribute for robustness
                tc_function = getattr(tool_call, "function", None)
                if not tc_function:
                    continue

                tool_name = tc_function.name
                try:
                    tool_args = json.loads(tc_function.arguments)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse tool arguments for {tool_name}: {e}")
                    tool_calls_made.append({
                        "id": tool_call.id,
                        "tool": tool_name,
                        "arguments": tc_function.arguments,
                        "result": {"success": False, "error": f"Invalid JSON arguments: {e}"}
                    })
                    continue

                logger.info(f"Calling MCP SDK tool: {tool_name} with args: {tool_args}")

                # Resolve numeric references in tool_args
                if "todo_id" in tool_args:
                    tool_args["todo_id"] = resolve_todo_id(str(tool_args["todo_id"]))

                # Prepare context for MCP tool call
                mcp_args = {
                    **tool_args,
                    "user_id": user_id,
                    "jwt_token": jwt_token
                }

                try:
                    if mcp_app is not None and CallToolRequest is not None:
                        # Execute via MCP Protocol layer (CallToolRequest)
                        mcp_request = CallToolRequest(name=tool_name, arguments=mcp_args)
                        mcp_results = await mcp_app.call_tool(mcp_request)

                        # MCP returns a list of content blocks
                        tool_result = mcp_results[0] if mcp_results else {"success": False, "error": "No result from tool"}
                    else:
                        # Direct tool invocation (used in unit tests)
                        tool_fn = getattr(mcp_tools, tool_name)
                        tool_result = await tool_fn(**mcp_args)

                    tool_calls_made.append({
                        "id": tool_call.id,
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": tool_result
                    })
                except Exception as e:
                    logger.error(f"Tool execution failed: {e}")
                    tool_calls_made.append({
                        "id": tool_call.id,
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": {"success": False, "error": str(e)}
                    })

        # Get final response content
        if tool_calls_made:
            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["tool"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls_made
                ]
            })

            # Add tool results to conversation
            for tc in tool_calls_made:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(tc["result"])
                })

            # Get final response with tool results
            final_response = await openai_client.chat.completions.create(
                model=AGENT_MODEL,
                messages=messages, # type: ignore
                temperature=AGENT_TEMPERATURE,
                max_tokens=AGENT_MAX_TOKENS
            )

            response_content = final_response.choices[0].message.content or "I've completed your request."
        else:
            # No tools called, use direct response
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
        # Return a useful error message instead of generic one
        error_msg = str(e)

        # Provide helpful response based on error type
        if "api" in error_msg.lower() or "key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            response_text = "I'm having trouble connecting to the AI service. Please try again in a moment."
        elif "rate" in error_msg.lower() or "429" in error_msg:
            response_text = "I'm getting too many requests. Please wait a moment and try again."
        else:
            response_text = f"I encountered an issue: {error_msg[:100]}"

        return {
            "content": response_text,
            "metadata": {
                "error": str(e),
                "tool_calls": []
            }
        }
