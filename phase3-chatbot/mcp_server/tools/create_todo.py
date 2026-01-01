"""
MCP Tool: create_todo

Creates a new todo item for the authenticated user.

Spec Reference: specs/api/mcp-tools.md - Tool 1: create_todo
Task: 2.5
"""

from typing import Optional, Dict, Union
import httpx
from mcp_server.client import get_client


async def create_todo(
    user_id: Union[int, str],  # Accept both int and UUID string
    title: str,
    description: Optional[str] = None,
    priority: Optional[str] = "medium",
    due_date: Optional[str] = None,
    jwt_token: Optional[str] = None
) -> Dict:
    """
    Create a new todo item

    Args:
        user_id: ID of the authenticated user (from JWT token)
        title: Title of the todo (required, max 200 chars)
        description: Detailed description (optional, max 1000 chars)
        priority: Priority level (optional, defaults to 'medium')
        due_date: Due date in ISO 8601 format (optional)

    Returns:
        Dict with success status, created todo, and message

    Raises:
        None - All errors returned in response dict
    """
    try:
        # Input validation
        # Convert user_id to string (it's a UUID from JWT)
        user_id_str = str(user_id)
        if not user_id_str:
            return {
                "success": False,
                "error": "Invalid user_id",
                "code": "VALIDATION_ERROR"
            }

        if not title or len(title.strip()) == 0:
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

        if description and len(description) > 1000:
            return {
                "success": False,
                "error": "Description exceeds maximum length of 1000 characters",
                "code": "VALIDATION_ERROR"
            }

        if priority and priority not in ["low", "medium", "high"]:
            return {
                "success": False,
                "error": f"Invalid priority: {priority}. Must be low, medium, or high",
                "code": "VALIDATION_ERROR"
            }

        # Prepare request to Phase 2 backend
        # Phase 2 TaskCreate schema only accepts title and description
        payload = {
            "title": title.strip()
        }

        if description:
            payload["description"] = description.strip()

        # Note: priority and due_date are not supported by Phase 2 backend yet

        # Call Phase 2 backend (using Phase 2's actual endpoint format)
        # Pass JWT token for authentication
        client = get_client(jwt_token=jwt_token)
        response = await client.client.post(f"/api/{user_id_str}/tasks", json=payload)

        if response.status_code == 201 or response.status_code == 200:
            todo = response.json()
            return {
                "success": True,
                "todo": todo,
                "message": "Todo created successfully"
            }
        else:
            error_data = response.json() if response.text else {}
            return {
                "success": False,
                "error": error_data.get("detail", "Failed to create todo"),
                "code": "BACKEND_ERROR"
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out while creating todo",
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
