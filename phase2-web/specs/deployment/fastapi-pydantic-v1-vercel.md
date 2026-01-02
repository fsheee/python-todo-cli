# FastAPI + Pydantic v1 Vercel Deployment Specification

> **Version:** 2.0
> **Last Updated:** 2025-12-14
> **Status:** Active

---

## Goal

Enable a working FastAPI backend on Vercel that:
- Does not crash at import time
- Supports JWT authentication
- Exposes RESTful API endpoints
- Can be consumed by a Next.js frontend deployed on Vercel

---

## Constraints

| Constraint | Requirement |
|------------|-------------|
| FastAPI | Must be pinned to Pydantic v1–compatible version |
| Pydantic | Must use v1.x (no Pydantic v2 or pydantic-core) |
| Runtime | Python serverless functions via Vercel |
| Entry Point | Must use Vercel's `api/index.py` pattern |
| ORM | SQLModel (Pydantic v1 compatible) |
| Database | Pure Python driver (no native extensions) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              VERCEL                                      │
├─────────────────────────────┬───────────────────────────────────────────┤
│   Next.js Frontend          │   FastAPI Backend (Serverless)            │
│   (/app, /components)       │   (/api/index.py)                         │
│                             │                                            │
│   - Server Components       │   - Pydantic v1 schemas                   │
│   - Client Components       │   - SQLModel ORM                          │
│   - API Client (fetch)      │   - JWT Authentication                    │
│                             │   - pg8000 PostgreSQL driver              │
└─────────────────────────────┴───────────────────────────────────────────┘
                                         │
                                         │ SQL (pg8000)
                                         ▼
                              ┌───────────────────────┐
                              │   Neon PostgreSQL     │
                              │   (Serverless DB)     │
                              └───────────────────────┘
```

---

## Package Dependencies

### requirements.txt

```
# Vercel-compatible requirements (Pydantic v1 - NO BINARY DEPENDENCIES)
fastapi==0.99.1
pydantic==1.10.13
starlette==0.27.0
uvicorn==0.23.2
python-dotenv==1.0.0
pyjwt==2.8.0
bcrypt==4.0.1
pg8000==1.30.3
sqlalchemy==1.4.50
sqlmodel==0.0.8
httpx==0.25.0
```

### Package Justification

| Package | Version | Why This Version |
|---------|---------|------------------|
| `fastapi` | 0.99.1 | Last version with native Pydantic v1 support |
| `pydantic` | 1.10.13 | Pure Python, no `pydantic-core` binary |
| `starlette` | 0.27.0 | Required by FastAPI 0.99.1 |
| `sqlmodel` | 0.0.8 | Uses Pydantic v1 internally |
| `sqlalchemy` | 1.4.50 | Required by SQLModel 0.0.8 |
| `pg8000` | 1.30.3 | Pure Python PostgreSQL driver |
| `pyjwt` | 2.8.0 | Pure Python JWT library |
| `bcrypt` | 4.0.1 | Password hashing (has binary but works on Vercel) |

### Forbidden Packages

| Package | Reason |
|---------|--------|
| `pydantic>=2.0` | Requires `pydantic-core` (Rust binary) |
| `psycopg2` | Requires libpq C library |
| `psycopg2-binary` | Binary incompatible with Lambda |
| `asyncpg` | Requires C compilation |
| `sqlalchemy>=2.0` | May pull in incompatible dependencies |

---

## Vercel Configuration

### vercel.json

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### api/index.py (Entry Point)

```python
"""Vercel serverless entry point."""
from main import app
```

This simple import exposes the FastAPI `app` instance to Vercel's Python runtime.

---

## SQLModel Configuration

### models.py

```python
"""SQLModel database models (Pydantic v1 compatible)."""

from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True)
    hashed_password: Optional[str] = Field(default=None)
    email_verified: bool = Field(default=False)
    name: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Task(SQLModel, table=True):
    """Task model for user todo items."""

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
```

### db.py (Database Connection)

```python
"""Database connection using pg8000 pure Python driver."""

import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # SQLite fallback for local development
    DATABASE_URL = "sqlite:///./todo.db"
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    # Convert to pg8000 driver format for Neon PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )


def create_db_and_tables():
    """Create all database tables from SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency that provides a database session."""
    with Session(engine) as session:
        yield session
```

---

## Pydantic v1 Schema Syntax

### Key Differences from Pydantic v2

| Feature | Pydantic v2 (NOT ALLOWED) | Pydantic v1 (REQUIRED) |
|---------|---------------------------|------------------------|
| Config | `model_config = {...}` | `class Config: ...` |
| Validators | `@field_validator("field")` | `@validator("field")` |
| ORM Mode | `from_attributes=True` | `orm_mode = True` |
| Optional | `str \| None` | `Optional[str]` |
| List | `list[Item]` | `List[Item]` |

### schemas.py

```python
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


# Auth Schemas
class RegisterInput(BaseModel):
    """Schema for user registration."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=255)

    @validator("email")
    def email_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v


class LoginInput(BaseModel):
    """Schema for user login."""

    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=1)

    @validator("email")
    def email_normalize(cls, v: str) -> str:
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
```

---

## JWT Authentication

### Token Configuration

```python
import os
import jwt
from datetime import datetime, timezone, timedelta

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "dev-secret-32-chars-minimum!!")
TOKEN_EXPIRE_HOURS = 24
ALGORITHM = "HS256"
```

### Token Creation

```python
def create_token(user: User) -> str:
    """Create a JWT token for authenticated user."""
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=ALGORITHM)
```

### Token Verification

```python
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
    """Verify JWT token and return payload."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create new user | No |
| POST | `/api/auth/login` | Authenticate user | No |
| POST | `/api/auth/logout` | End session | No |
| GET | `/api/auth/session` | Get current user | Yes |

### Tasks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/{user_id}/tasks` | List all tasks | Yes |
| POST | `/api/{user_id}/tasks` | Create task | Yes |
| GET | `/api/{user_id}/tasks/{id}` | Get single task | Yes |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Yes |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | Yes |

### Health Check

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |

---

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://python-todo-cli-d9n6.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

## Environment Variables

### Backend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Neon PostgreSQL connection string |
| `BETTER_AUTH_SECRET` | Yes | JWT signing secret (32+ characters) |

### Frontend (Vercel)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend URL (e.g., `https://backend.vercel.app`) |
| `BETTER_AUTH_SECRET` | Yes | Same as backend |
| `BETTER_AUTH_URL` | Yes | Frontend URL |

---

## File Structure

```
backend/
├── api/
│   └── index.py          # Vercel serverless entry point
├── routes/
│   ├── auth.py           # Authentication endpoints
│   └── tasks.py          # Task CRUD endpoints
├── main.py               # FastAPI application
├── models.py             # SQLModel database models
├── schemas.py            # Pydantic v1 schemas
├── db.py                 # Database connection (pg8000)
├── auth.py               # JWT utilities
├── requirements.txt      # Pydantic v1 dependencies
├── pyproject.toml        # Project configuration
└── vercel.json           # Vercel deployment config
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] `requirements.txt` has Pydantic v1 packages
- [ ] `pyproject.toml` has matching versions
- [ ] `schemas.py` uses Pydantic v1 syntax (`@validator`, `orm_mode`)
- [ ] `models.py` uses `Optional[]` not `| None`
- [ ] `uv.lock` is deleted (prevents version conflicts)
- [ ] `vercel.json` points to `api/index.py`
- [ ] `api/index.py` imports `from main import app`

### Vercel Dashboard

- [ ] Set `DATABASE_URL` environment variable
- [ ] Set `BETTER_AUTH_SECRET` environment variable
- [ ] Deploy from GitHub

### Post-Deployment

- [ ] Test `/health` endpoint returns `{"status": "healthy"}`
- [ ] Test `/api/auth/login` returns JWT token
- [ ] Update frontend `NEXT_PUBLIC_API_URL`
- [ ] Redeploy frontend

---

## Verification Commands

```bash
# Health check
curl https://your-backend.vercel.app/health

# Register user
curl -X POST https://your-backend.vercel.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Login
curl -X POST https://your-backend.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get tasks (with token)
curl https://your-backend.vercel.app/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}"
```

---

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`

**Cause:** Pydantic v2 is being installed instead of v1.

**Fix:**
1. Verify `requirements.txt` has `pydantic==1.10.13`
2. Delete `uv.lock` file
3. Redeploy

### Error: `TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument`

**Cause:** Python version incompatibility with Pydantic v1.

**Fix:** Ensure using Python 3.11 (not 3.12+) or update Pydantic to `1.10.13`

### Error: `sqlalchemy.exc.OperationalError: connection refused`

**Cause:** Database connection issue.

**Fix:**
1. Verify `DATABASE_URL` is set in Vercel
2. Check pg8000 driver prefix (`postgresql+pg8000://`)
3. Verify Neon database is active

---

## Related Specifications

- `specs/api/rest-endpoints.md` - API endpoint details
- `specs/database/schema.md` - Database schema
- `specs/features/authentication.md` - Auth flow
- `specs/deployment/frontend-backend-integration.md` - Integration guide
