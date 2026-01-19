"""
MCP Tool: update_todo

Updates an existing todo item.

Spec Reference: specs/api/mcp-tools.md - Tool 3: update_todo
Task: 2.7
"""

from typing import Optional, Dict, List, Union
import inspect
from mcp_server.client import get_client
import httpx


class _HttpClientProxy:
    def put(self, path: str, **kwargs):
        jwt_token = kwargs.pop("jwt_token", None)
        client = get_client(jwt_token=jwt_token)
        return client.client.put(path, **kwargs)


http_client = _HttpClientProxy()


async def update_todo(
    user_id: Union[int, str],
    todo_id: Union[int, str],
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    jwt_token: Optional[str] = None
) -> Dict:
    """
    Update an existing todo item

    Args:
        user_id: ID of the authenticated user (from JWT token)
        todo_id: ID of the todo to update
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)
        priority: New priority (optional)
        due_date: New due date in ISO 8601 format (optional)

    Returns:
        Dict with success status, updated todo, message, and changes list

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

        # Build update payload with only provided fields
        updates: Dict[str, str] = {}
        changes: List[str] = []

        if title is not None:
            if len(title.strip()) == 0:
                return {
                    "success": False,
                    "error": "Title cannot be empty",
                    "code": "VALIDATION_ERROR"
                }
            if len(title) > 200:
                return {
                    "success": False,
                    "error": "Title exceeds maximum length of 200 characters",
                    "code": "VALIDATION_ERROR"
                }
            updates["title"] = title.strip()
            changes.append("title")

        if description is not None:
            if description and len(description) > 1000:
                return {
                    "success": False,
                    "error": "Description exceeds maximum length",
                    "code": "VALIDATION_ERROR"
                }
            updates["description"] = description.strip() if description else ""
            changes.append("description")

        if status is not None:
            if status not in ["pending", "completed"]:
                return {
                    "success": False,
                    "error": f"Invalid status: {status}",
                    "code": "VALIDATION_ERROR"
                }
            # Phase 2 backend might not support status field in TodoUpdate yet
            # but we pass it anyway
            updates["status"] = status
            changes.append("status")

        if priority is not None:
            if priority not in ["low", "medium", "high"]:
                return {
                    "success": False,
                    "error": f"Invalid priority: {priority}",
                    "code": "VALIDATION_ERROR"
                }
            updates["priority"] = priority
            changes.append("priority")

        if due_date is not None:
            updates["due_date"] = due_date
            changes.append("due_date")

        # Note: priority and due_date are not supported by Phase 2 backend yet

        # Check if there are any updates
        if not changes:
            return {
                "success": False,
                "error": "No fields to update",
                "code": "VALIDATION_ERROR"
            }

        # Call Phase 2 backend
        # Phase 2 backend uses /api/{user_id}/tasks/{task_id}
        endpoint = f"/api/{user_id_str}/tasks/{todo_id_str}"
        response = http_client.put(endpoint, json=updates, jwt_token=jwt_token)
        if inspect.isawaitable(response):
            response = await response

        if response.status_code == 200:
            todo = response.json()
            return {
                "success": True,
                "todo": todo,
                "message": "Todo updated successfully",
                "changes": changes
            }
        elif response.status_code == 404:
            return {
                "success": False,
                "error": "Todo not found or access denied",
                "code": "NOT_FOUND"
            }
        else:
            return {
                "success": False,
                "error": "Failed to update todo",
                "code": "BACKEND_ERROR"
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out while updating todo",
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
