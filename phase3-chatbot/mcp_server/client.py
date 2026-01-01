"""
HTTP Client for communicating with Phase 2 Backend

Spec Reference: specs/api/mcp-tools.md - Service Authentication
Task: 2.4
"""

import httpx
from typing import Optional
from mcp_server.config import config


class Phase2Client:
    """Async HTTP client for Phase 2 backend communication"""

    def __init__(self, jwt_token: Optional[str] = None):
        """Initialize HTTP client with connection pooling

        Args:
            jwt_token: Optional JWT token for user authentication
        """
        # Use JWT token if provided (for user auth), otherwise use service token
        auth_header = f"Bearer {jwt_token}" if jwt_token else f"Bearer {config.INTERNAL_SERVICE_TOKEN}"

        self.client = httpx.AsyncClient(
            base_url=config.PHASE2_API_URL,
            timeout=httpx.Timeout(config.HTTP_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            headers={
                "Authorization": auth_header,
                "X-Internal-Service": "mcp-server",
                "Content-Type": "application/json"
            }
        )

    async def close(self):
        """Close HTTP client connections"""
        await self.client.aclose()

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()


# Global client instance
_client: Optional[Phase2Client] = None


def get_client(jwt_token: Optional[str] = None) -> Phase2Client:
    """Get or create HTTP client instance with JWT token

    Args:
        jwt_token: JWT token for user authentication

    Returns:
        Phase2Client instance with authentication
    """
    # Always create new client with JWT token for proper user authentication
    # Don't use global client since each request may have different user
    return Phase2Client(jwt_token=jwt_token)


async def close_client():
    """Close global HTTP client"""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
