"""
Authentication routes for Phase 3 chatbot
Uses local auth against Neon PostgreSQL (Better Auth schema)
"""

import os
import logging
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "default-secret-key-change-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 30


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


def create_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please check your email or sign up."
        )

    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No password set for this account."
        )

    if not bcrypt.checkpw(credentials.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password."
        )

    token = create_token(str(user.id), user.email)
    logger.info(f"User logged in: {user.email}")

    return AuthResponse(
        access_token=token,
        user={"id": str(user.id), "email": user.email, "name": user.name}
    )


@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: SignupRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing = result.scalars().first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered. Please login instead."
        )

    hashed = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user = User(
        email=user_data.email,
        hashed_password=hashed,
        name=user_data.name,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id), user.email)
    logger.info(f"User registered: {user.email}")

    return AuthResponse(
        access_token=token,
        user={"id": str(user.id), "email": user.email, "name": user.name}
    )


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}


@router.get("/health")
async def auth_health(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "auth": "local", "database": "connected"}
    except Exception:
        return {"status": "degraded", "auth": "local", "database": "disconnected"}
