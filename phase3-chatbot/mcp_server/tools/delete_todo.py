"""
MCP Tool: delete_todo

Deletes a todo item with confirmation requirement.

Spec Reference: specs/api/mcp-tools.md - Tool 4: delete_todo
Task: 2.8
"""

from typing import Dict
from mcp_server.client import get_client
import httpx


async def delete_todo(
    user_id: int,
    todo_id: int,
    confirm: bool = False
) -> Dict:
    """
    Delete a todo item

    Args:
        user_id: ID of the authenticated user (from JWT token)
        todo_id: ID of the todo to delete
        confirm: Confirmation flag (must be true for deletion to proceed)

    Returns:
        Dict with success status, deleted todo details, and message

    Raises:
        None - All errors returned in response dict
    """
    try:
        # Input validation
        if not user_id or user_id <= 0:
            return {
                "success": False,
                "error": "Invalid user_id",
                "code": "VALIDATION_ERROR"
            }

        if not todo_id or todo_id <= 0:
            return {
                "success": False,
                "error": "Invalid todo_id",
                "code": "VALIDATION_ERROR"
            }

        # Safety check: require confirmation
        if not confirm:
            return {
                "success": False,
                "error": "Deletion requires confirmation. Set confirm=true to proceed.",
                "code": "CONFIRMATION_REQUIRED"
            }

        # First, fetch the todo to get its details for confirmation message
        client = get_client()
        get_response = await client.client.get(
            f"/todos/{todo_id}",
            params={"user_id": user_id}
        )

        if get_response.status_code != 200:
            return {
                "success": False,
                "error": "Todo not found or access denied",
                "code": "NOT_FOUND"
            }

        todo = get_response.json()

        # Delete the todo
        delete_response = await client.client.delete(
            f"/todos/{todo_id}",
            params={"user_id": user_id}
        )

        if delete_response.status_code == 200 or delete_response.status_code == 204:
            return {
                "success": True,
                "message": "Todo deleted successfully",
                "deleted_todo": {
                    "id": todo.get("id"),
                    "title": todo.get("title")
                }
            }
        else:
            return {
                "success": False,
                "error": "Failed to delete todo",
                "code": "BACKEND_ERROR"
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out while deleting todo",
            "code": "TIMEOUT"
        }
    except httpx.ConnectError:
        return {
            "success": False,
            "error": "Could not connect to backend service",
            "code": "SERVICE_UNAVAILABLE"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Internal error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
