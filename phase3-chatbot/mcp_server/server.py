"""
MCP Server Implementation

Main MCP server that registers all todo management tools and handles
communication with the AI agent.

Spec Reference: specs/api/mcp-tools.md - MCP Server Implementation
Tasks: 2.2, 2.4
"""

import asyncio
import logging
from mcp import Server
from mcp.server import stdio_server

from mcp_server.config import config
from mcp_server.tools import (
    create_todo,
    list_todos,
    update_todo,
    delete_todo,
    search_todos
)

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server(config.SERVER_NAME)


# Register tools
@app.tool()
async def create_todo_tool(
    user_id: int,
    title: str,
    description: str = None,
    priority: str = "medium",
    due_date: str = None
) -> dict:
    """
    Create a new todo item for the authenticated user

    Args:
        user_id: ID of the authenticated user (from JWT token)
        title: Title of the todo (required, max 200 chars)
        description: Detailed description (optional, max 1000 chars)
        priority: Priority level (optional: low, medium, high)
        due_date: Due date in ISO 8601 format (optional)

    Returns:
        Dict with success status and created todo
    """
    return await create_todo(user_id, title, description, priority, due_date)


@app.tool()
async def list_todos_tool(
    user_id: int,
    status: str = "pending",
    priority: str = None,
    due_date: str = None,
    due_date_range: str = None,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """
    Retrieve todos for the authenticated user with optional filters

    Args:
        user_id: ID of the authenticated user (from JWT token)
        status: Filter by status (pending, completed, all)
        priority: Filter by priority (low, medium, high)
        due_date: Filter by specific due date
        due_date_range: Filter by relative range (today, tomorrow, this_week, etc.)
        limit: Maximum results (default 50, max 100)
        offset: Pagination offset (default 0)

    Returns:
        Dict with success status and todos array
    """
    return await list_todos(user_id, status, priority, due_date, due_date_range, limit, offset)


@app.tool()
async def update_todo_tool(
    user_id: int,
    todo_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    due_date: str = None
) -> dict:
    """
    Update an existing todo item

    Args:
        user_id: ID of the authenticated user (from JWT token)
        todo_id: ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional: pending, completed)
        priority: New priority (optional: low, medium, high)
        due_date: New due date in ISO 8601 format (optional)

    Returns:
        Dict with success status and updated todo
    """
    return await update_todo(user_id, todo_id, title, description, status, priority, due_date)


@app.tool()
async def delete_todo_tool(
    user_id: int,
    todo_id: int,
    confirm: bool = False
) -> dict:
    """
    Delete a todo item (requires confirmation)

    Args:
        user_id: ID of the authenticated user (from JWT token)
        todo_id: ID of the todo to delete
        confirm: Confirmation flag (must be true)

    Returns:
        Dict with success status and deleted todo details
    """
    return await delete_todo(user_id, todo_id, confirm)


@app.tool()
async def search_todos_tool(
    user_id: int,
    query: str,
    status: str = "all",
    limit: int = 20
) -> dict:
    """
    Search todos by keyword

    Args:
        user_id: ID of the authenticated user (from JWT token)
        query: Search keyword or phrase
        status: Filter by status (optional: pending, completed, all)
        limit: Maximum results (default 20, max 50)

    Returns:
        Dict with success status and matching todos
    """
    return await search_todos(user_id, query, status, limit)


async def main():
    """Run the MCP server"""
    logger.info(f"Starting {config.SERVER_NAME} v{config.SERVER_VERSION}")

    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    logger.info(f"Connected to Phase 2 backend at: {config.PHASE2_API_URL}")
    logger.info("Registered 5 MCP tools: create_todo, list_todos, update_todo, delete_todo, search_todos")

    # Run server
    async with stdio_server(app):
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
