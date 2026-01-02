"""
MCP Tool: search_todos

Searches todos by keyword in title and description.

Spec Reference: specs/api/mcp-tools.md - Tool 5: search_todos
Task: 2.9
"""

from typing import Optional, Dict
from mcp_server.client import get_client
import httpx


async def search_todos(
    user_id: int,
    query: str,
    status: Optional[str] = "all",
    limit: int = 20
) -> Dict:
    """
    Search todos by keyword

    Args:
        user_id: ID of the authenticated user (from JWT token)
        query: Search keyword or phrase
        status: Filter results by status (optional, defaults to 'all')
        limit: Maximum number of results (default 20, max 50)

    Returns:
        Dict with success status, matching todos array, count, and query

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

        if not query or len(query.strip()) == 0:
            return {
                "success": False,
                "error": "Search query cannot be empty",
                "code": "VALIDATION_ERROR"
            }

        if len(query) > 100:
            query = query[:100]  # Truncate long queries

        if status and status not in ["pending", "completed", "all"]:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "code": "VALIDATION_ERROR"
            }

        if limit > 50:
            limit = 50

        # Clean and prepare query
        clean_query = query.strip()

        # Build parameters
        params = {
            "user_id": user_id,
            "q": clean_query,
            "limit": limit
        }

        if status and status != "all":
            params["status"] = status

        # Call Phase 2 backend search endpoint
        client = get_client()
        response = await client.client.get("/todos/search", params=params)

        if response.status_code == 200:
            data = response.json()
            todos = data if isinstance(data, list) else data.get("todos", [])

            return {
                "success": True,
                "todos": todos,
                "count": len(todos),
                "query": clean_query
            }
        else:
            return {
                "success": False,
                "error": "Search failed",
                "code": "BACKEND_ERROR"
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Request timed out while searching todos",
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
