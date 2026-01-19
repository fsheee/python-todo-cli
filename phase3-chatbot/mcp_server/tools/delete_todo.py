"""
MCP Tool: delete_todo

Deletes a todo item with confirmation requirement.

Spec Reference: specs/api/mcp-tools.md - Tool 4: delete_todo
Task: 2.8
"""

from typing import Dict, Optional, Union
import inspect
from mcp_server.client import get_client
import httpx


class _HttpClientProxy:
    def get(self, path: str, **kwargs):
        jwt_token = kwargs.pop("jwt_token", None)
        client = get_client(jwt_token=jwt_token)
        return client.client.get(path, **kwargs)

    def delete(self, path: str, **kwargs):
        jwt_token = kwargs.pop("jwt_token", None)
        client = get_client(jwt_token=jwt_token)
        return client.client.delete(path, **kwargs)


http_client = _HttpClientProxy()


async def delete_todo(
    user_id: Union[int, str],
    todo_id: Union[int, str],
    confirm: bool = False,
    jwt_token: Optional[str] = None
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
        # Phase 2 uses UUID strings, but tests may provide ints
        if isinstance(user_id, int):
            if user_id <= 0:
                return {
                    "success": False,
                    "error": "Invalid user_id",
                    "code": "VALIDATION_ERROR"
                }
            user_id_str = str(user_id)
        else:
            user_id_str = str(user_id).strip()
            if not user_id_str:
                return {
                    "success": False,
                    "error": "Invalid user_id",
                    "code": "VALIDATION_ERROR"
                }

        todo_id_str = str(todo_id)
        if not todo_id_str:
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
        # Phase 2 backend uses /api/{user_id}/tasks/{task_id}
        get_endpoint = f"/api/{user_id_str}/tasks/{todo_id_str}"
        get_response = http_client.get(get_endpoint, jwt_token=jwt_token)
        if inspect.isawaitable(get_response):
            get_response = await get_response

        if get_response.status_code != 200:
            return {
                "success": False,
                "error": "Todo not found or access denied",
                "code": "NOT_FOUND"
            }

        todo = get_response.json()

        # Delete the todo
        delete_endpoint = f"/api/{user_id_str}/tasks/{todo_id_str}"
        delete_response = http_client.delete(delete_endpoint, jwt_token=jwt_token)
        if inspect.isawaitable(delete_response):
            delete_response = await delete_response

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
