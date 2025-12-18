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

    def __init__(self):
        """Initialize HTTP client with connection pooling"""
        self.client = httpx.AsyncClient(
            base_url=config.PHASE2_API_URL,
            timeout=httpx.Timeout(config.HTTP_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
            headers={
                "Authorization": f"Bearer {config.INTERNAL_SERVICE_TOKEN}",
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


def get_client() -> Phase2Client:
    """Get or create global HTTP client instance"""
    global _client
    if _client is None:
        _client = Phase2Client()
    return _client


async def close_client():
    """Close global HTTP client"""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
