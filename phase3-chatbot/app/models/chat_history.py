"""ChatHistory SQLModel for storing conversation messages."""

from sqlmodel import SQLModel, Field, Column, JSON
from datetime import datetime
from typing import Optional, Dict, Any


class ChatHistory(SQLModel, table=True):
    """
    Chat history model for storing conversation messages

    Spec Reference: specs/database/chat-history.md
    """
    __tablename__ = "chat_history"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False)

    # Session Management
    session_id: str = Field(index=True, nullable=False, max_length=100)

    # Message Content
    role: str = Field(nullable=False, max_length=20)  # "user", "assistant", "system"
    content: str = Field(nullable=False)  # Message text

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )  # Store tool calls, tokens used, etc.

    # Timestamps
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Soft Delete
    is_deleted: bool = Field(default=False, nullable=False)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "session_id": "sess_abc123xyz",
                "role": "user",
                "content": "Show me my tasks",
                "metadata": {
                    "client_ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0..."
                },
                "timestamp": "2025-12-18T10:30:00Z",
                "is_deleted": False
            }
        }
