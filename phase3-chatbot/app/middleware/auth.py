"""
JWT authentication middleware for chat endpoint

Spec Reference: specs/overview.md - Authentication Flow

Task: 4.2
"""

import os
import jwt
import httpx
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

PHASE2_API_URL = os.getenv("PHASE2_API_URL", "http://localhost:8000").rstrip("/")

# Better Auth secret (from Phase 2)
# Keep default aligned with Phase 2 backend for local dev.
BETTER_AUTH_SECRET = (os.getenv("BETTER_AUTH_SECRET") or "dev-secret-key-minimum-32-characters-long").strip()

# HTTP Bearer security scheme
security = HTTPBearer()


async def verify_jwt_token(credentials: HTTPAuthorizationCredentials) -> str:
    """
    Verify JWT token and extract user_id

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        user_id: Authenticated user's ID (UUID string from Phase 2)

    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        token = credentials.credentials
        logger.info(f"Verifying token: {token[:20]}...")
        logger.info(f"Using secret: {BETTER_AUTH_SECRET[:10] if BETTER_AUTH_SECRET else 'NOT SET'}...")

        # Decode JWT using Better Auth secret
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        logger.info(f"Token decoded successfully. Payload keys: {payload.keys()}")

        # Extract user_id (UUID from Phase 2 Better Auth)
        user_id = payload.get("sub") or payload.get("user_id")

        logger.info(f"Extracted user_id: {user_id}")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        # Return user_id as string (UUID format from Phase 2)
        return str(user_id)

    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        # If we can't verify locally, try delegating validation to Phase 2.
        # This helps when Phase 3 is configured to proxy auth to a deployed Phase 2.
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{PHASE2_API_URL}/api/auth/session",
                    headers={"Authorization": f"Bearer {token}"},
                )

            if resp.status_code == 200:
                data = resp.json()
                user = data.get("user") or {}
                user_id = user.get("id")
                if user_id:
                    logger.info("Token validated via Phase 2 /api/auth/session")
                    return str(user_id)
        except Exception as phase2_err:
            logger.error(f"Phase 2 token validation failed: {phase2_err}")

        logger.error(f"Invalid token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ValueError as e:
        logger.error(f"ValueError during auth: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    except Exception as e:
        logger.error(f"Unexpected auth error: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


