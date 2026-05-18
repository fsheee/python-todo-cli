"""
Task model for Phase 3 database.
"""

from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model stored in Phase 3 database."""

    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: str = Field(default="pending")
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = Field(default=None)
    user_id: str = Field(max_length=100, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)