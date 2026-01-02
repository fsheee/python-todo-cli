# Prompt History - Backend

> Auto-logged user instructions for audit, context reuse, and collaboration.

---

## Session: 2025-12-11

### PHR-001: Initialize Backend Auth Routes
**Timestamp:** 2025-12-11T16:00:00Z
**Type:** Implementation

Add authentication routes to backend - register, login, logout, session endpoints.

**Output:** Created `routes/auth.py` with JWT authentication

---

### PHR-002: Add Password Hashing
**Timestamp:** 2025-12-11T16:15:00Z
**Type:** Implementation

Add bcrypt password hashing for user registration and login.

**Output:** Added bcrypt dependency, implemented `hash_password()` and `verify_password()` functions

---

### PHR-003: Update User Model
**Timestamp:** 2025-12-11T16:20:00Z
**Type:** Implementation

Add `hashed_password` field to User model for storing password hashes.

**Output:** Updated `models.py` with `hashed_password` field

---

### PHR-004: Add Auth Schemas
**Timestamp:** 2025-12-11T16:25:00Z
**Type:** Implementation

Create Pydantic schemas for auth requests/responses - RegisterInput, LoginInput, AuthResponse, UserResponse.

**Output:** Updated `schemas.py` with auth schemas

---

### PHR-005: Database Migration
**Timestamp:** 2025-12-11T16:30:00Z
**Type:** Setup

Add `hashed_password` column to existing users table in Neon PostgreSQL.

**Output:** Ran ALTER TABLE to add column

---

### PHR-006: Register Auth Router
**Timestamp:** 2025-12-11T16:35:00Z
**Type:** Implementation

Register auth router in main.py FastAPI application.

**Output:** Updated `main.py` to include auth_router

---

### PHR-007: Install bcrypt Dependency
**Timestamp:** 2025-12-11T21:30:00Z
**Type:** Setup

Install bcrypt package using uv add for password hashing.

**Output:** Added bcrypt to pyproject.toml dependencies

---

## Session: 2026-01-02

### PHR-008: Fix Model Name Inconsistency
**Timestamp:** 2026-01-02T01:30:00Z
**Type:** Bug Fix

Fixed NameError in routes/tasks.py where Task model was referenced but models.py had renamed it to Todo.

**Context:** User reported errors after 2 days of working code. Git history showed model rename from Task to Todo in commit history.

**Output:** Updated all 7 references in `routes/tasks.py` from `Task` to `Todo`
- Lines 85-87: List query `select(Todo)`
- Line 115: Get task `session.get(Todo, task_id)`
- Line 150: Update task `session.get(Todo, task_id)`
- Line 198: Delete task `session.get(Todo, task_id)`
- Line 233: Toggle completion `session.get(Todo, task_id)`

**Related Files:**
- `phase2-web/backend/routes/tasks.py`
- `phase2-web/backend/models.py`

---

### PHR-009: Add Database Connection Pooling for Neon
**Timestamp:** 2026-01-02T02:15:00Z
**Type:** Enhancement

Added connection pooling configuration for Neon PostgreSQL serverless to prevent SSL connection drops.

**Context:** Users experienced `psycopg2.OperationalError: SSL connection has been closed unexpectedly` errors when Phase 3 MCP tools called Phase 2 backend.

**Output:** Updated `db.py` with connection pool settings:
```python
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Test connections before use (critical for Neon)
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=10,        # Connection pool size
    max_overflow=20      # Allow overflow connections
)
```

**Related Files:**
- `phase2-web/backend/db.py`

**References:**
- Neon serverless requires connection validation before use
- psycopg2-binary driver already installed

---

### PHR-010: Verify JWT Authentication Chain
**Timestamp:** 2026-01-02T02:45:00Z
**Type:** Verification

Verified Phase 2 backend correctly validates JWT tokens from Phase 3 chatbot requests.

**Context:** Phase 3 MCP tools were receiving 401 Unauthorized errors. Needed to verify Phase 2 auth middleware was working correctly.

**Findings:**
- Phase 2 auth endpoints (`/api/auth/register`, `/api/auth/login`) return JWT tokens correctly
- JWT tokens contain user_id as UUID string
- Auth dependency in routes validates Bearer tokens
- Task routes correctly filter by `current_user.id` from JWT

**Verification Method:**
- Tested signup/login flow generates valid JWT
- Confirmed JWT contains user UUID
- Verified task CRUD operations use authenticated user_id

**Related Files:**
- `phase2-web/backend/routes/auth.py`
- `phase2-web/backend/routes/tasks.py`
- `phase2-web/backend/middleware/auth.py` (if exists)

---

