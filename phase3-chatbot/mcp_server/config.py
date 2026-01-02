"""
Configuration module for MCP Server

Loads configuration from environment variables and provides defaults
for development.

Spec Reference: specs/api/mcp-tools.md - Configuration
Task: 2.3
"""

import os
from typing import Optional


class Config:
    """MCP Server configuration"""

    # Phase 2 Backend API URL
    PHASE2_API_URL: str = os.getenv(
        "PHASE2_API_URL",
        "http://localhost:8000"  # Default for local development
    )

    # Internal service token for authenticating to Phase 2 backend
    INTERNAL_SERVICE_TOKEN: Optional[str] = os.getenv("INTERNAL_SERVICE_TOKEN")

    # MCP Server settings
    SERVER_NAME: str = "todo-mcp-server"
    SERVER_VERSION: str = "1.0.0"

    # HTTP client settings
    HTTP_TIMEOUT: int = int(os.getenv("HTTP_TIMEOUT", "30"))  # seconds
    HTTP_RETRY_ATTEMPTS: int = int(os.getenv("HTTP_RETRY_ATTEMPTS", "3"))
    HTTP_RETRY_DELAY: int = int(os.getenv("HTTP_RETRY_DELAY", "1"))  # seconds

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration

        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.INTERNAL_SERVICE_TOKEN:
            raise ValueError(
                "INTERNAL_SERVICE_TOKEN environment variable is required"
            )

        if not cls.PHASE2_API_URL:
            raise ValueError(
                "PHASE2_API_URL environment variable is required"
            )


# Global config instance
config = Config()
