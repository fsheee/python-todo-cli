"""Authentication API routes.

Implements endpoints per /specs/features/authentication.md:
- POST   /api/auth/register    - Create new user account
- POST   /api/auth/login       - Authenticate user
- POST   /api/auth/logout      - End session
- GET    /api/auth/session     - Get current user info
"""

import os
from datetime import datetime, timezone, timedelta
from uuid import UUID

import jwt
from passlib.hash import pbkdf2_sha256
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from dotenv import load_dotenv

from db import get_session
from models import User
from schemas import RegisterInput, LoginInput, AuthResponse, UserResponse

load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["auth"])

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "dev-secret-key-minimum-32-characters-long")
TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pbkdf2_sha256.verify(password, hashed)


def create_token(user: User) -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
async def register(
    data: RegisterInput,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """Register a new user account.

    - Email must be unique
    - Password is hashed before storage
    - Returns JWT token on success
    """
    # Check if email already exists
    existing = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create user with hashed password
    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate token
    token = create_token(user)

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, name=user.name),
        token=token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    data: LoginInput,
    session: Session = Depends(get_session),
) -> AuthResponse:
    """Authenticate with email and password.

    - Returns JWT token on success
    - Returns 401 for invalid credentials
    """
    # Find user by email
    user = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate token
    token = create_token(user)

    return AuthResponse(
        user=UserResponse(id=user.id, email=user.email, name=user.name),
        token=token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful"},
    },
)
async def logout() -> dict:
    """End current session.

    Note: With JWT, logout is primarily client-side (discard token).
    This endpoint exists for API consistency.
    """
    return {"message": "Successfully signed out"}


@router.get(
    "/session",
    response_model=dict,
    responses={
        200: {"description": "Session info"},
        401: {"description": "Not authenticated"},
    },
)
async def get_session_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> dict:
    """Get current session/user info.

    - Validates JWT token
    - Returns user info if valid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"],
        )
        user_id = UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Get user from database
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {
        "user": UserResponse(id=user.id, email=user.email, name=user.name),
        "expires_at": payload.get("exp"),
    }
