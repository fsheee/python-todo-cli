"""Pydantic v1 schemas for request/response validation."""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)

    @validator("title")
    def title_not_blank(cls, v: str) -> str:
        """Validate title is not blank after trimming."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Title cannot be blank")
        return stripped


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)

    @validator("title")
    def title_not_blank(cls, v: Optional[str]) -> Optional[str]:
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
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: List[TaskResponse]
    count: int


class ErrorDetail(BaseModel):
    """Schema for field-level error detail."""

    field: str
    message: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    detail: str
    errors: Optional[List[ErrorDetail]] = None


# Auth Schemas
class RegisterInput(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)

    @validator("email")
    def email_valid(cls, v: str) -> str:
        """Validate and normalize email."""
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

    @validator("name")
    def name_not_blank(cls, v: str) -> str:
        """Validate name is not blank."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name cannot be blank")
        return stripped


class LoginInput(BaseModel):
    """Schema for user login."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)

    @validator("email")
    def email_normalize(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.strip().lower()


class UserResponse(BaseModel):
    """Schema for user in response."""

    id: UUID
    email: str
    name: Optional[str]

    class Config:
        orm_mode = True


class AuthResponse(BaseModel):
    """Schema for auth response with token."""

    user: UserResponse
    token: str
