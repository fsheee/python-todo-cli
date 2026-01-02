"""
Authentication routes for Phase 3 chatbot

Proxies authentication to Phase 2 Better Auth backend (reusing Phase 2 logic)
Spec Reference: specs/overview.md - Authentication (Reused from Phase 2)
"""

import os
import logging
import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Phase 2 backend URL (remove trailing slash if present)
PHASE2_API_URL = os.getenv("PHASE2_API_URL", "http://localhost:8000").rstrip("/")

# Cache for backend health status
_backend_healthy = None
_last_check = 0


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """Signup request model"""
    email: EmailStr
    password: str
    name: str  # Required - will default to email prefix if not provided


class AuthResponse(BaseModel):
    """Authentication response model"""
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest):
    """
    Login user via Phase 2 Better Auth backend

    Args:
        credentials: User email and password

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        HTTPException: If login fails
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Call Phase 2 login endpoint - CORRECT PATH: /api/auth/login
            response = await client.post(
                f"{PHASE2_API_URL}/api/auth/login",
                json={
                    "email": credentials.email,
                    "password": credentials.password
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"User logged in successfully: {credentials.email}")
                return AuthResponse(
                    access_token=data.get("token") or data.get("access_token"),
                    token_type="bearer",
                    user=data.get("user", {})
                )
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found. Please check your email or sign up."
                )
            else:
                logger.error(f"Phase 2 auth error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Authentication service unavailable"
                )

    except httpx.TimeoutException:
        logger.error("Phase 2 backend timeout during login")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Authentication service timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Phase 2 backend request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to authentication service"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: SignupRequest):
    """
    Register new user via Phase 2 Better Auth backend

    Args:
        user_data: User registration data

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        HTTPException: If signup fails
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Call Phase 2 register endpoint - CORRECT PATH: /api/auth/register
            response = await client.post(
                f"{PHASE2_API_URL}/api/auth/register",
                json={
                    "email": user_data.email,
                    "password": user_data.password,
                    "name": user_data.name
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"User registered successfully: {user_data.email}")
                return AuthResponse(
                    access_token=data.get("token") or data.get("access_token"),
                    token_type="bearer",
                    user=data.get("user", {})
                )
            elif response.status_code == 409:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered. Please login instead."
                )
            else:
                logger.error(f"Phase 2 signup error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Registration service unavailable"
                )

    except httpx.TimeoutException:
        logger.error("Phase 2 backend timeout during signup")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Registration service timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Phase 2 backend request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to registration service"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token removal)

    Returns:
        Success message
    """
    return {"message": "Logged out successfully"}


@router.get("/health")
async def auth_health():
    """
    Health check for authentication service

    Returns:
        Health status of Phase 2 backend connection
    """
    import time

    current_time = time.time()
    global _backend_healthy, _last_check

    # Only check every 10 seconds to avoid spamming
    if current_time - _last_check > 10:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{PHASE2_API_URL}/health", follow_redirects=True)
                _backend_healthy = response.status_code == 200
        except Exception as e:
            logger.error(f"Phase 2 backend health check failed: {e}")
            _backend_healthy = False
        finally:
            _last_check = current_time

    return {
        "status": "healthy" if _backend_healthy else "degraded",
        "phase2_backend": PHASE2_API_URL,
        "connected": _backend_healthy
    }
