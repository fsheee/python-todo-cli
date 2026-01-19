"""
MCP Tool: search_todos

Searches todos by keyword in title and description.

Spec Reference: specs/api/mcp-tools.md - Tool 5: search_todos
Task: 2.9
"""

from typing import Optional, Dict, Union
import inspect
from mcp_server.client import get_client
import httpx


class _HttpClientProxy:
    def get(self, path: str, **kwargs):
        jwt_token = kwargs.pop("jwt_token", None)
        client = get_client(jwt_token=jwt_token)
        return client.client.get(path, **kwargs)


http_client = _HttpClientProxy()


async def search_todos(
    user_id: Union[int, str],
    query: str,
    status: Optional[str] = "all",
    limit: int = 20,
    jwt_token: Optional[str] = None
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
            "q": clean_query,
            "limit": limit
        }

        if status and status != "all":
            params["status"] = status

        # Call Phase 2 backend search endpoint
        # Phase 2 backend uses /api/{user_id}/tasks/search
        endpoint = f"/api/{user_id_str}/tasks/search"
        response = http_client.get(endpoint, params=params, jwt_token=jwt_token)
        if inspect.isawaitable(response):
            response = await response

        if response.status_code == 200:
            data = response.json()
            # Phase 2 backend returns {"tasks": [...], "count": N}
            if isinstance(data, list):
                todos = data
            else:
                todos = data.get("tasks") or data.get("todos") or []

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
