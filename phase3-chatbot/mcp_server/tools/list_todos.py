"""
MCP Tool: list_todos

Retrieves user's todos with optional filters.

Spec Reference: specs/api/mcp-tools.md - Tool 2: list_todos
Task: 2.6
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from mcp_server.client import get_client
import httpx


def calculate_date_range(range_type: str) -> Dict:
    """
    Convert relative date range to start/end dates

    Args:
        range_type: Relative range (today, tomorrow, this_week, etc.)

    Returns:
        Dict with date filter parameters
    """
    today = datetime.now().date()

    if range_type == "today":
        return {"due_date": today.isoformat()}
    elif range_type == "tomorrow":
        return {"due_date": (today + timedelta(days=1)).isoformat()}
    elif range_type == "this_week":
        week_end = today + timedelta(days=(6 - today.weekday()))
        return {"due_date_start": today.isoformat(), "due_date_end": week_end.isoformat()}
    elif range_type == "next_week":
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        return {"due_date_start": next_week_start.isoformat(), "due_date_end": next_week_end.isoformat()}
    elif range_type == "overdue":
        return {"due_date_end": (today - timedelta(days=1)).isoformat(), "status": "pending"}
    else:
        return {}


async def list_todos(
    user_id: int,
    status: Optional[str] = "pending",
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
    due_date_range: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict:
    """
    Retrieve todos for the authenticated user with optional filters

    Args:
        user_id: ID of the authenticated user (from JWT token)
        status: Filter by status (optional, defaults to 'pending')
        priority: Filter by priority (optional)
        due_date: Filter by specific due date (optional)
        due_date_range: Filter by relative date range (optional)
        limit: Maximum number of results (default 50, max 100)
        offset: Number of results to skip for pagination (default 0)

    Returns:
        Dict with success status, todos array, count, and pagination info

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

        if status and status not in ["pending", "completed", "all"]:
            return {
                "success": False,
                "error": f"Invalid status: {status}. Must be pending, completed, or all",
                "code": "VALIDATION_ERROR"
            }

        if priority and priority not in ["low", "medium", "high"]:
            return {
                "success": False,
                "error": f"Invalid priority: {priority}",
                "code": "VALIDATION_ERROR"
            }

        if limit > 100:
            limit = 100

        # Build query parameters
        params = {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        }

        if status and status != "all":
            params["status"] = status

        if priority:
            params["priority"] = priority

        # Handle date filters
        if due_date_range:
            date_filter = calculate_date_range(due_date_range)
            params.update(date_filter)
        elif due_date:
            params["due_date"] = due_date

        # Call Phase 2 backend
        client = get_client()
        response = await client.client.get("/todos", params=params)

        if response.status_code == 200:
            data = response.json()
            todos = data if isinstance(data, list) else data.get("todos", [])

            return {
                "success": True,
                "todos": todos,
                "count": len(todos),
                "total": data.get("total", len(todos)) if isinstance(data, dict) else len(todos),
                "has_more": len(todos) == limit
            }
        else:
            return {
                "success": False,
                "error": "Failed to retrieve todos",
                "code": "BACKEND_ERROR"
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out while retrieving todos",
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
