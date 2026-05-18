"""
Pydantic schemas for tasks API

Provides REST endpoints for task CRUD operations.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TaskCreate(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(default=None, max_length=1000, description="Task description (optional)")
    priority: Optional[str] = Field(default="medium", description="Priority: low, medium, or high")
    due_date: Optional[str] = Field(default=None, description="Due date in ISO 8601 format")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy milk",
                "description": "Get 2% milk from the store",
                "priority": "medium",
                "due_date": "2025-12-25T10:00:00Z"
            }
        }


class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[str] = Field(default=None, description="Status: pending, in_progress, completed")
    priority: Optional[str] = Field(default=None, description="Priority: low, medium, or high")
    due_date: Optional[str] = Field(default=None, description="Due date in ISO 8601 format")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy milk (updated)",
                "status": "completed",
                "priority": "high"
            }
        }


class TaskResponse(BaseModel):
    """Response schema for a single task"""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: str = Field(default="pending", description="Task status")
    priority: str = Field(default="medium", description="Task priority")
    due_date: Optional[str] = Field(default=None, description="Due date")
    user_id: str = Field(..., description="Owner user ID")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task_123",
                "title": "Buy milk",
                "description": "Get 2% milk",
                "status": "pending",
                "priority": "medium",
                "user_id": "user_456",
                "created_at": "2025-12-19T10:00:00Z",
                "updated_at": "2025-12-19T10:00:00Z"
            }
        }


class TaskListResponse(BaseModel):
    """Response schema for listing tasks"""
    tasks: List[TaskResponse] = Field(default_factory=list, description="List of tasks")
    total: int = Field(default=0, description="Total number of tasks")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=50, description="Items per page")

    class Config:
        json_schema_extra = {
            "example": {
                "tasks": [],
                "total": 0,
                "page": 1,
                "page_size": 50
            }
        }