"""
User model aligned with Phase 2 Better Auth database schema
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid


class User(SQLModel, table=True):
    """User model matching Better Auth 'users' table"""
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    email_verified: bool = Field(default=False, nullable=False)
    name: Optional[str] = Field(default=None)
    image: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    hashed_password: Optional[str] = Field(default=None)
