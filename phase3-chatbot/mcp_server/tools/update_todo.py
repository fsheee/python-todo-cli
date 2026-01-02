"""
MCP Tool: update_todo

Updates an existing todo item.

Spec Reference: specs/api/mcp-tools.md - Tool 3: update_todo
Task: 2.7
"""

from typing import Optional, Dict, List
from mcp_server.client import get_client
import httpx


async def update_todo(
    user_id: int,
    todo_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
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

        # Build update payload with only provided fields
        updates = {"user_id": user_id}
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
            updates["description"] = description.strip() if description else None
            changes.append("description")

        if status is not None:
            if status not in ["pending", "completed"]:
                return {
                    "success": False,
                    "error": f"Invalid status: {status}",
                    "code": "VALIDATION_ERROR"
                }
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

        # Check if there are any updates
        if not changes:
            return {
                "success": False,
                "error": "No fields to update",
                "code": "VALIDATION_ERROR"
            }

        # Call Phase 2 backend
        client = get_client()
        response = await client.client.put(f"/todos/{todo_id}", json=updates)

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
