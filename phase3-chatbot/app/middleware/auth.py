"""
JWT authentication middleware for chat endpoint

Spec Reference: specs/overview.md - Authentication Flow
Task: 4.2
"""

import os
import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

# Better Auth secret (from Phase 2)
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# HTTP Bearer security scheme
security = HTTPBearer()


async def verify_jwt_token(credentials: HTTPAuthorizationCredentials) -> int:
    """
    Verify JWT token and extract user_id

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        user_id: Authenticated user's ID

    Raises:
        HTTPException: If token is invalid, expired, or missing
    """
    try:
        token = credentials.credentials

        # Decode JWT using Better Auth secret
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )

        # Extract user_id
        user_id = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        # Return user_id as integer
        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
