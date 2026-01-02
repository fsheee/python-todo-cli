# Prompt History

> Auto-logged user instructions for audit, context reuse, and collaboration.

---

## Session: 2025-12-10

### PHR-001: Generate Task CRUD Feature Specification
**Timestamp:** 2025-12-10T21:30:00Z
**Type:** Specification

Generate a detailed feature specification in markdown for "Task CRUD" for a multi-user todo web app. Include sections: User Stories, Acceptance Criteria, Edge Cases, API requirements, Database/model notes, UI considerations.

**Output:** `specs/features/task-crud.md`

---

### PHR-002: Create All Remaining Specs
**Timestamp:** 2025-12-10T21:45:00Z
**Type:** Specification

Create all referenced spec files:
- `specs/api/rest-endpoints.md`
- `specs/database/schema.md`
- `specs/features/authentication.md`
- `specs/agents/todo-agent.md`
- `specs/agents/skills/*.md` (7 skill specs)
- `specs/ui/components.md`
- `specs/ui/pages.md`

**Output:** 14 specification files created

---

### PHR-003: Implement Backend Task CRUD
**Timestamp:** 2025-12-10T22:00:00Z
**Type:** Implementation

Implement Task CRUD feature in backend per `specs/features/task-crud.md`.

**Output:** Backend files created:
- `backend/db.py` - Database connection
- `backend/models.py` - SQLModel models
- `backend/schemas.py` - Pydantic schemas
- `backend/auth.py` - JWT authentication
- `backend/routes/tasks.py` - Task CRUD routes
- `backend/main.py` - FastAPI entry point

---

### PHR-004: Setup UV Python Project
**Timestamp:** 2025-12-10T22:05:00Z
**Type:** Setup

Create uv Python project, add dependencies, activate venv.

**Output:**
- `pyproject.toml` created
- Dependencies: fastapi, sqlmodel, psycopg, python-dotenv, pyjwt, uvicorn
- Virtual environment at `.venv/`

---

### PHR-005: Fix Environment Configuration
**Timestamp:** 2025-12-10T22:10:00Z
**Type:** Bugfix

Fix DATABASE_URL format in `.env` (removed `psql '...'` wrapper), changed driver to `postgresql+psycopg://`.

**Output:** Server running successfully at http://127.0.0.1:8000

---

### PHR-006: Create Test User
**Timestamp:** 2025-12-10T22:12:00Z
**Type:** Setup

Create test user in database for foreign key constraint.

**Output:** User created with ID `550e8400-e29b-41d4-a716-446655440000`

---

### PHR-007: Generate JWT Token
**Timestamp:** 2025-12-10T22:27:00Z
**Type:** Setup

Generate valid JWT token for API testing.

**Output:** Token valid for 7 days

---

### PHR-008: API Testing Successful
**Timestamp:** 2025-12-10T22:35:00Z
**Type:** Verification

All Task CRUD endpoints tested and working:
- POST /api/{user_id}/tasks - 201 Created
- GET /api/{user_id}/tasks - 200 OK
- GET /api/{user_id}/tasks/{id} - 200 OK
- PUT /api/{user_id}/tasks/{id} - 200 OK
- DELETE /api/{user_id}/tasks/{id} - 204 No Content
- PATCH /api/{user_id}/tasks/{id}/complete - 200 OK

---

### PHR-009: Create Prompt Logger Agent
**Timestamp:** 2025-12-10T22:40:00Z
**Type:** Specification

Create prompt history file and Prompt Logger Agent spec.

**Output:**
- `.claude/prompt-history.md` - Session prompt history
- `specs/agents/prompt-logger-agent.md` - Agent specification

---

### PHR-010: Add Pytest and Create Tests
**Timestamp:** 2025-12-10T23:00:00Z/resume
**Type:** Implementation

Add pytest dependencies and create comprehensive test suite for Task CRUD API.

**Dependencies Added:**
- pytest
- pytest-asyncio
- httpx

**Output:**
- `tests/__init__.py`
- `tests/conftest.py` - Test fixtures and mocked auth
- `tests/test_tasks.py` - 27 test cases

**Test Results:** 27 passed

---

## Session: 2025-12-14

### PHR-011: Deploy Backend to Vercel
**Timestamp:** 2025-12-14T16:00:00Z
**Type:** Deployment

Deploy FastAPI backend to Vercel serverless.

**Tasks Completed:**
1. Created `vercel.json` for Python serverless configuration
2. Generated `requirements.txt` from `pyproject.toml` using `uv pip compile`
3. Updated CORS in `main.py` to allow Vercel frontend domains
4. Created `api/index.py` entry point (Vercel preferred pattern)
5. Fixed binary dependency issues:
   - Replaced `psycopg2-binary` with `pg8000` (pure Python PostgreSQL driver)
   - Updated `db.py` to convert DATABASE_URL for pg8000 driver

**Output:**
- Backend deployed: `https://python-todo-cli-bakend.vercel.app`
- Files created/modified:
  - `backend/vercel.json`
  - `backend/requirements.txt`
  - `backend/api/index.py`
  - `backend/db.py` (pg8000 driver support)
  - `backend/main.py` (CORS update)

---

### PHR-012: Configure Frontend-Backend Integration
**Timestamp:** 2025-12-14T17:00:00Z
**Type:** Configuration

Connect Vercel frontend to Vercel backend.

**Environment Variables Required:**
- Frontend: `NEXT_PUBLIC_API_URL=https://python-todo-cli-bakend.vercel.app`
- Backend: `DATABASE_URL` (Neon PostgreSQL connection string)
- Backend: `BETTER_AUTH_SECRET` (JWT secret, 32+ chars)

**Frontend URL:** `https://python-todo-cli-d9n6.vercel.app`

---

### PHR-013: Debug Vercel Serverless Crash
**Timestamp:** 2025-12-14T19:00:00Z
**Type:** Debugging

Investigating FUNCTION_INVOCATION_FAILED errors on backend.

**Possible Causes:**
- Missing environment variables (DATABASE_URL, BETTER_AUTH_SECRET)
- Database connection timeout
- Cold start issues on free tier

**Status:** In Progress - Awaiting Vercel logs from user

---
