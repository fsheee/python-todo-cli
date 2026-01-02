"""
Local authentication service
Fallback when Phase 2 Better Auth is unavailable
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlmodel import Session, select
from app.models.user import User

# JWT Configuration
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", "default-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def register_user(session: Session, email: str, password: str, name: Optional[str] = None) -> Dict:
    """
    Register a new user

    Args:
        session: Database session
        email: User email
        password: Plain password
        name: Optional user name

    Returns:
        Dict with access_token and user data

    Raises:
        ValueError: If email already exists
    """
    # Check if user exists
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise ValueError("Email already registered")

    # Create new user
    password_hash = hash_password(password)
    user = User(
        email=email,
        password_hash=password_hash,
        name=name,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token
    access_token = create_access_token(user.id, user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    }


async def authenticate_user(session: Session, email: str, password: str) -> Dict:
    """
    Authenticate user and return token

    Args:
        session: Database session
        email: User email
        password: Plain password

    Returns:
        Dict with access_token and user data

    Raises:
        ValueError: If credentials are invalid
    """
    # Find user
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        raise ValueError("Account not found")

    if not user.is_active:
        raise ValueError("Account is disabled")

    # Verify password
    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid password")

    # Update last login
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()

    # Generate JWT token
    access_token = create_access_token(user.id, user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    }
