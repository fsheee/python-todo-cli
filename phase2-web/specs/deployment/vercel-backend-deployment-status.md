# Vercel Backend Deployment Status

> **Version:** 1.0
> **Last Updated:** 2025-12-15
> **Status:** Stable

---

## Deployment Summary

| Item | Value |
|------|-------|
| Platform | Vercel Python Serverless Functions |
| Runtime | Python 3.12 (Vercel-managed) |
| Framework | FastAPI 0.99.1 |
| ORM | SQLModel 0.0.8 + SQLAlchemy 1.4.41 |
| Validation | Pydantic 1.10.18 (v1) |
| Database | Neon PostgreSQL (pg8000 driver) |
| Dependency Manager | uv with uv.lock |

---

## Build Status

| Check | Status |
|-------|--------|
| `vercel build` completes | ✅ Pass |
| Dependencies installed from uv.lock | ✅ Pass |
| No dependency resolution errors | ✅ Pass |
| Deployment completes | ✅ Pass |

---

## Known Warnings (Non-Blocking)

### Warning 1: Build Settings Override

```
WARN! Due to `builds` existing in your configuration file, the Build and
Development Settings defined in your Project Settings will not apply.
```

**Status:** Expected behavior
**Impact:** None
**Reason:** `vercel.json` contains explicit `builds` configuration, which takes precedence over dashboard settings. This is intentional.

### Warning 2: Python Version Constraint Ignored

```
Warning: Python version ">=3.11,<3.12" detected in pyproject.toml is not
installed and will be ignored.
```

**Status:** Accepted
**Impact:** None
**Reason:** Vercel uses its managed Python 3.12 runtime. The constraint in `pyproject.toml` is for local development. Pydantic 1.10.18 is compatible with Python 3.12.

---

## Runtime Configuration

### vercel.json

```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.11"
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

### pyproject.toml

```toml
[project]
name = "todo-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.99.1",
    "pydantic==1.10.18",
    "sqlmodel==0.0.8",
    "sqlalchemy==1.4.41",
    "uvicorn==0.23.2",
    "python-dotenv==1.0.0",
    "pyjwt==2.8.0",
    "bcrypt==4.0.1",
    "pg8000==1.30.3",
    "httpx==0.25.0",
]
```

---

## Acceptance Criteria

| Criterion | Status | Notes |
|-----------|--------|-------|
| `vercel build` completes successfully | ✅ | Build logs show completion |
| No dependency resolution errors | ✅ | uv.lock used successfully |
| Backend responds to HTTP requests | 🔄 Pending | Requires validation |
| `/docs` endpoint loads correctly | 🔄 Pending | Requires validation |
| No import-time crashes on cold start | 🔄 Pending | Requires validation |

---

## Validation Commands

Run these after deployment to confirm acceptance criteria:

```bash
# Health check
curl -s https://python-todo-cli-bakend.vercel.app/health

# OpenAPI docs
curl -s -o /dev/null -w "%{http_code}" https://python-todo-cli-bakend.vercel.app/docs

# API root
curl -s https://python-todo-cli-bakend.vercel.app/
```

**Expected Results:**
- `/health` returns `{"status": "healthy"}`
- `/docs` returns HTTP 200
- No 500 errors on cold start

---

## Environment Variables Required

| Variable | Required | Set in Vercel |
|----------|----------|---------------|
| `DATABASE_URL` | Yes | Must be configured |
| `BETTER_AUTH_SECRET` | Yes | Must be configured |

---

## Constraints (Documented)

| Constraint | Description |
|------------|-------------|
| Python Runtime | Vercel-managed Python 3.12 |
| Dependency Resolution | Must use uv.lock |
| No Docker | Serverless functions only |
| Pydantic Version | Must remain v1 (1.10.18) |
| No Platform Change | Vercel only |

---

## Non-Goals (Out of Scope)

- Changing deployment platform
- Altering Python runtime selection
- Modifying vercel.json build behavior
- Migrating to Pydantic v2

---

## Frontend Integration

Once backend is validated, update frontend:

1. Set `NEXT_PUBLIC_API_URL` in Vercel frontend project
2. Value: `https://python-todo-cli-bakend.vercel.app`
3. Redeploy frontend

---

## Related Files

| File | Purpose |
|------|---------|
| `backend/vercel.json` | Vercel deployment configuration |
| `backend/pyproject.toml` | Python project dependencies |
| `backend/uv.lock` | Locked dependency versions |
| `backend/api/index.py` | Serverless entry point |
| `backend/main.py` | FastAPI application |
| `backend/requirements.txt` | Fallback dependencies |

---

## Deployment History

| Date | Commit | Status | Notes |
|------|--------|--------|-------|
| 2025-12-15 | `93f5611` | Deployed | Pydantic 1.10.18, Python 3.12 compat |
