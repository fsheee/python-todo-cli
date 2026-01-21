"""
Pydantic schemas for chat API

Spec Reference: specs/PLAN.md - Frontend ↔ Backend Integration
Task: 4.1
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    session_id: str | None = Field(None, min_length=1, max_length=100, description="Chat session ID (optional, will be generated if missing)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add buy milk to my list",
                "session_id": "sess_1702890000_a7f3k9x2"
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    response: str = Field(..., description="AI assistant's response")
    session_id: str = Field(..., description="Chat session ID")
    timestamp: str = Field(..., description="Response timestamp in ISO 8601 format")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "I've added 'Buy milk' to your list. 📝",
                "session_id": "sess_1702890000_a7f3k9x2",
                "timestamp": "2025-12-19T10:30:00Z"
            }
        }
