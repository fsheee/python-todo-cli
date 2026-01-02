# ADR-003: API Design Pattern

**Status:** Accepted
**Date:** 2025-12-10
**Decision Makers:** Claude, User

---

## Context

Need to design REST API endpoints for task management that are secure, intuitive, and follow best practices.

## Decision

Use **user-scoped REST endpoints** with the pattern:
```
/api/{user_id}/tasks
/api/{user_id}/tasks/{task_id}
```

## Rationale

### Why user_id in URL?
- Explicit resource ownership
- Clearer API semantics
- Easier to audit and log
- Supports future admin/impersonation features

### Security Model
- JWT token must contain matching user_id
- Backend verifies token user_id matches URL user_id
- Returns 403 Forbidden if mismatch
- Returns 404 Not Found if task doesn't belong to user

### HTTP Methods
| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/api/{user_id}/tasks` | Create task |
| GET | `/api/{user_id}/tasks` | List tasks |
| GET | `/api/{user_id}/tasks/{task_id}` | Get task |
| PUT | `/api/{user_id}/tasks/{task_id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{task_id}/complete` | Toggle completion |

## Consequences

### Positive
- RESTful and predictable
- Strong security boundary
- Easy to understand and document
- Supports future multi-user features

### Negative
- Slightly longer URLs
- Client must know user_id (obtained from JWT)

## Alternatives Considered

1. **`/api/tasks` (user from token only)** - Less explicit, harder to debug
2. **GraphQL** - Overkill for simple CRUD
3. **`/api/me/tasks`** - Semantic but non-standard

---
