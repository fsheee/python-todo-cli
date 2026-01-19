"""
Pydantic schemas for chat history API

Spec Reference: specs/features/chatbot.md - Feature 8: Context and Memory
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """Schema for a single chat message"""
    role: str = Field(..., description="Message role (user, assistant, system, tool)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp in ISO 8601 format")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class MessageListResponse(BaseModel):
    """Response schema for listing messages in a session"""
    messages: List[MessageResponse] = Field(..., description="List of messages")
    total: int = Field(..., description="Total number of messages in session")
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User ID")
    has_more: bool = Field(..., description="Whether there are more messages to load")
