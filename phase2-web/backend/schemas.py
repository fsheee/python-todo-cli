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


# Auth Schemas
class RegisterInput(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        """Validate and normalize email."""
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator("name")
    @classmethod
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

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.strip().lower()


class UserResponse(BaseModel):
    """Schema for user in response."""

    id: UUID
    email: str
    name: str | None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    """Schema for auth response with token."""

    user: UserResponse
    token: str
