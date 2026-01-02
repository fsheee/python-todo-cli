"""JWT authentication utilities for Better Auth integration."""

import os
from uuid import UUID
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Use a default secret for local development only
if not BETTER_AUTH_SECRET:
    BETTER_AUTH_SECRET = "dev-secret-key-minimum-32-characters-long"

security = HTTPBearer()


class AuthenticatedUser:
    """Represents an authenticated user from JWT token."""

    def __init__(self, id: UUID, email: str | None = None, name: str | None = None):
        self.id = id
        self.email = email
        self.name = name


def verify_jwt_token(token: str) -> dict:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthenticatedUser:
    """FastAPI dependency to get the current authenticated user.

    Args:
        credentials: HTTP Bearer credentials from request

    Returns:
        AuthenticatedUser object

    Raises:
        HTTPException: If authentication fails
    """
    payload = verify_jwt_token(credentials.credentials)

    try:
        user_id = UUID(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing or invalid user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(
        id=user_id,
        email=payload.get("email"),
        name=payload.get("name"),
    )


def verify_user_access(
    current_user: AuthenticatedUser,
    user_id: UUID,
) -> None:
    """Verify that the authenticated user matches the requested user_id.

    Args:
        current_user: The authenticated user from JWT
        user_id: The user_id from the URL path

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user ID mismatch",
        )


async def get_verified_user(
    user_id: Annotated[UUID, Path(description="User ID from URL")],
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """FastAPI dependency that verifies the URL user_id matches the JWT user.

    Args:
        user_id: User ID from URL path
        current_user: Authenticated user from JWT

    Returns:
        AuthenticatedUser if verification passes

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    verify_user_access(current_user, user_id)
    return current_user
