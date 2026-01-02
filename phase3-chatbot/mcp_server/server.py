"""
MCP Server Implementation

Main MCP server that registers all todo management tools and handles
communication with the AI agent.

Spec Reference: specs/api/mcp-tools.md - MCP Server Implementation
Tasks: 2.2, 2.4
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# MCP imports - try different import paths for compatibility
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError:
    from mcp import Server
    from mcp.server.stdio import stdio_server

from mcp.types import Tool as MCPTool, ListToolsRequest, CallToolRequest

# Import all todo tools
from mcp_server.tools.create_todo import create_todo
from mcp_server.tools.list_todos import list_todos
from mcp_server.tools.update_todo import update_todo
from mcp_server.tools.delete_todo import delete_todo
from mcp_server.tools.search_todos import search_todos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-server")

# Initialize MCP server
app = Server("todo-mcp-server")


def create_mcp_tools():
    """Create MCP tool definitions from todo tool functions"""

    # create_todo tool
    create_todo_schema = MCPTool(
        name="create_todo",
        description="Create a new todo item for the authenticated user. Returns the created todo with its ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the authenticated user (from JWT token)"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the todo (required, max 200 chars)",
                    "maxLength": 200
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the todo (optional, max 1000 chars)",
                    "maxLength": 1000
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Priority level (optional, defaults to 'medium')"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Due date in ISO 8601 format (optional)"
                }
            },
            "required": ["user_id", "title"]
        }
    )

    # list_todos tool
    list_todos_schema = MCPTool(
        name="list_todos",
        description="Retrieve todos for the authenticated user with optional filters for status, priority, and due date.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the authenticated user (from JWT token)"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by status (optional, defaults to 'pending')"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Filter by priority (optional)"
                },
                "due_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Filter by due date (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (optional, default 50, max 100)",
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["user_id"]
        }
    )

    # update_todo tool
    update_todo_schema = MCPTool(
        name="update_todo",
        description="Update an existing todo item. Only provided fields will be updated.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the authenticated user (from JWT token)"
                },
                "todo_id": {
                    "type": "integer",
                    "description": "ID of the todo to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title (optional)",
                    "maxLength": 200
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed"],
                    "description": "New status (optional)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New priority (optional)"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "New due date (optional)"
                }
            },
            "required": ["user_id", "todo_id"]
        }
    )

    # delete_todo tool
    delete_todo_schema = MCPTool(
        name="delete_todo",
        description="Delete a todo item. This action is permanent and cannot be undone.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the authenticated user (from JWT token)"
                },
                "todo_id": {
                    "type": "integer",
                    "description": "ID of the todo to delete"
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Confirmation flag (must be true for deletion to proceed)",
                    "default": False
                }
            },
            "required": ["user_id", "todo_id", "confirm"]
        }
    )

    # search_todos tool
    search_todos_schema = MCPTool(
        name="search_todos",
        description="Search todos by keyword. Searches in both title and description fields.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID of the authenticated user (from JWT token)"
                },
                "query": {
                    "type": "string",
                    "description": "Search keyword or phrase",
                    "minLength": 1,
                    "maxLength": 100
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter results by status (optional, defaults to 'all')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (optional, default 20, max 50)",
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["user_id", "query"]
        }
    )

    return [
        create_todo_schema,
        list_todos_schema,
        update_todo_schema,
        delete_todo_schema,
        search_todos_schema
    ]


# Create tool list
MCP_TOOLS = create_mcp_tools()


@app.list_tools()
async def list_tools(request: ListToolsRequest):
    """List all available MCP tools"""
    return MCP_TOOLS


@app.call_tool()
async def call_tool(request: CallToolRequest, extra: dict = None):
    """Handle tool calls from the AI agent"""
    name = request.name
    arguments = request.arguments

    logger.info(f"Tool called: {name} with args: {arguments}")

    try:
        if name == "create_todo":
            result = await create_todo(**arguments)
        elif name == "list_todos":
            result = await list_todos(**arguments)
        elif name == "update_todo":
            result = await update_todo(**arguments)
        elif name == "delete_todo":
            result = await delete_todo(**arguments)
        elif name == "search_todos":
            result = await search_todos(**arguments)
        else:
            result = {
                "success": False,
                "error": f"Unknown tool: {name}",
                "code": "UNKNOWN_TOOL"
            }

        logger.info(f"Tool result: {result}")
        return [result]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return [{
            "success": False,
            "error": f"Tool execution error: {str(e)}",
            "code": "TOOL_ERROR"
        }]


async def main():
    """Main entry point for MCP server"""
    logger.info("Starting MCP Todo Server...")
    logger.info(f"Python version: {sys.version}")

    try:
        async with stdio_server(app) as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("MCP Server shutting down...")
    except Exception as e:
        logger.error(f"MCP Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
