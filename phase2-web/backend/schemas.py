"""Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        """Validate title is not blank after trimming."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be blank")
        return stripped


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        """Validate title is not blank after trimming if provided."""
        if v is None:
            return v
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be blank")
        return stripped


class TaskResponse(BaseModel):
    """Schema for task response."""

    id: UUID
    user_id: UUID
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]
    count: int


class ErrorDetail(BaseModel):
    """Schema for field-level error detail."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    detail: str
    errors: list[ErrorDetail] | None = None
