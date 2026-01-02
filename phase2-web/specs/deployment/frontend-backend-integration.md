# Frontend-Backend Integration Specification

> **Version:** 1.0
> **Last Updated:** 2025-12-14
> **Status:** Active

---

## Overview

This document specifies how the Next.js frontend integrates with the FastAPI backend for the multi-user Todo application.

---

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│   Next.js Frontend  │  HTTPS  │   FastAPI Backend   │
│   (Vercel)          │◄───────►│   (Cloud Host)      │
│                     │  JSON   │                     │
│   Port: 443         │         │   Port: $PORT       │
└─────────────────────┘         └─────────────────────┘
                                         │
                                         │ SQL
                                         ▼
                                ┌─────────────────────┐
                                │   Neon PostgreSQL   │
                                │   (Cloud Database)  │
                                └─────────────────────┘
```

---

## Environment Configuration

### Frontend Environment Variables

| Variable | Local | Production | Description |
|----------|-------|------------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | `https://<backend-url>` | Backend API base URL |
| `BETTER_AUTH_SECRET` | (dev secret) | (same as backend) | JWT signing secret |
| `BETTER_AUTH_URL` | `http://localhost:3000` | `https://<frontend>.vercel.app` | Frontend base URL |

### Backend Environment Variables

| Variable | Local | Production | Description |
|----------|-------|------------|-------------|
| `DATABASE_URL` | (local DB) | Neon connection string | PostgreSQL connection |
| `BETTER_AUTH_SECRET` | (dev secret) | (same as frontend) | JWT signing secret |

**CRITICAL:** `BETTER_AUTH_SECRET` must be identical on both frontend and backend for JWT verification to work.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Create new user | No |
| POST | `/api/auth/login` | Authenticate user | No |
| POST | `/api/auth/logout` | End session | No |
| GET | `/api/auth/session` | Get current user | Yes |

### Tasks

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/{user_id}/tasks` | List all tasks | Yes |
| POST | `/api/{user_id}/tasks` | Create task | Yes |
| GET | `/api/{user_id}/tasks/{id}` | Get single task | Yes |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Yes |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | Yes |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion | Yes |

---

## Authentication Flow

```
┌──────────────┐                    ┌──────────────┐                    ┌──────────────┐
│   Frontend   │                    │   Backend    │                    │   Database   │
└──────┬───────┘                    └──────┬───────┘                    └──────┬───────┘
       │                                   │                                   │
       │  1. POST /api/auth/login          │                                   │
       │  { email, password }              │                                   │
       │──────────────────────────────────►│                                   │
       │                                   │  2. SELECT user WHERE email       │
       │                                   │─────────────────────────────────►│
       │                                   │◄─────────────────────────────────│
       │                                   │  3. Verify bcrypt password        │
       │                                   │  4. Generate JWT token            │
       │  5. { user, token }               │                                   │
       │◄──────────────────────────────────│                                   │
       │                                   │                                   │
       │  6. Store token in localStorage   │                                   │
       │                                   │                                   │
       │  7. GET /api/{user_id}/tasks      │                                   │
       │  Authorization: Bearer <token>    │                                   │
       │──────────────────────────────────►│                                   │
       │                                   │  8. Verify JWT                    │
       │                                   │  9. SELECT tasks WHERE user_id    │
       │                                   │─────────────────────────────────►│
       │                                   │◄─────────────────────────────────│
       │  10. { tasks: [...] }             │                                   │
       │◄──────────────────────────────────│                                   │
```

---

## JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "name": "User Name",
  "exp": 1702684800,
  "iat": 1702598400
}
```

- Token expires after 24 hours
- Algorithm: HS256
- Secret: `BETTER_AUTH_SECRET` environment variable

---

## CORS Configuration

Backend allows requests from:

```python
allow_origins=[
    "http://localhost:3000",           # Local development
    "https://python-todo-cli-d9n6.vercel.app",  # Production frontend
],
allow_origin_regex=r"https://.*\.vercel\.app",
allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
allow_headers=["Authorization", "Content-Type"],
allow_credentials=True,
```

---

## Frontend API Client

Location: `frontend/src/lib/api.ts`

Key Features:
- Single `ApiClient` class for all API calls
- Automatic token management (localStorage)
- Bearer token injection in all authenticated requests
- Error handling with typed `ApiError` responses

Usage:
```typescript
import { api } from '@/lib/api';

// Login
const response = await api.login({ email, password });
// Token automatically stored

// Get tasks (token automatically included)
const tasks = await api.getTasks(userId);
```

---

## Deployment Checklist

### Backend

1. [ ] Deploy backend to a Python-compatible cloud host
2. [ ] Set build command: `pip install -r requirements.txt`
3. [ ] Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. [ ] Add `DATABASE_URL` environment variable
5. [ ] Add `BETTER_AUTH_SECRET` environment variable
6. [ ] Deploy and note the URL

### Frontend (Vercel)

1. [ ] Deploy frontend to Vercel
2. [ ] Add `NEXT_PUBLIC_API_URL` with backend URL
3. [ ] Add `BETTER_AUTH_SECRET` (same as backend)
4. [ ] Add `BETTER_AUTH_URL` with Vercel frontend URL
5. [ ] Redeploy to apply environment variables

---

## Troubleshooting

### "Failed to sign in" Error

1. Check backend is running and accessible
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Check browser console for CORS errors
4. Verify database connection on backend

### 401 Unauthorized on Task Requests

1. Check token is stored in localStorage
2. Verify `BETTER_AUTH_SECRET` matches on both services
3. Check token hasn't expired (24 hour lifetime)
4. Ensure Authorization header is being sent

### CORS Errors

1. Verify frontend domain is in backend CORS config
2. Check `allow_credentials: true` is set
3. Ensure OPTIONS preflight requests are handled

---

## Related Files

- Frontend API Client: `frontend/src/lib/api.ts`
- Backend Main: `backend/main.py`
- Backend Auth Routes: `backend/routes/auth.py`
- Backend Task Routes: `backend/routes/tasks.py`
- Vercel Config: `backend/vercel.json`
