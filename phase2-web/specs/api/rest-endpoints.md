# REST API Endpoints Specification

> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

This document defines all REST API endpoints for the multi-user todo web application. All endpoints require JWT authentication and are user-scoped.

---

## Base URL

```
Production: https://api.todoapp.com
Development: http://localhost:8000
```

---

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### JWT Claims
| Claim | Type | Description |
|-------|------|-------------|
| `sub` | UUID | User ID |
| `exp` | timestamp | Expiration time |
| `iat` | timestamp | Issued at time |

### Authentication Errors
| Status | Code | Description |
|--------|------|-------------|
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 401 | `TOKEN_EXPIRED` | JWT token has expired |
| 403 | `FORBIDDEN` | User ID mismatch between URL and token |

---

## Task Endpoints

### POST /api/{user_id}/tasks

Create a new task.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |

**Request Body:**
```json
{
  "title": "string",
  "description": "string | null"
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `title` | Required, 1-255 characters, trimmed |
| `description` | Optional, max 2000 characters |

**Response: 201 Created**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Complete project documentation",
  "description": "Write API docs and user guide",
  "completed": false,
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T10:30:00Z"
}
```

**Headers:**
```
Location: /api/{user_id}/tasks/{task_id}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |
| 422 | Validation failed |

---

### GET /api/{user_id}/tasks

List all tasks for the authenticated user.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `completed` | boolean | - | Filter by completion status |
| `sort` | string | `created_at` | Sort field |
| `order` | string | `desc` | Sort order (asc/desc) |
| `limit` | integer | 50 | Max results (1-100) |
| `offset` | integer | 0 | Pagination offset |

**Response: 200 OK**
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Complete project documentation",
      "description": "Write API docs and user guide",
      "completed": false,
      "created_at": "2025-12-10T10:30:00Z",
      "updated_at": "2025-12-10T10:30:00Z"
    }
  ],
  "count": 1,
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |

---

### GET /api/{user_id}/tasks/{task_id}

Get a specific task by ID.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |
| `task_id` | UUID | Yes | ID of the task |

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Complete project documentation",
  "description": "Write API docs and user guide",
  "completed": false,
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T10:30:00Z"
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |
| 404 | Task not found or belongs to another user |
| 422 | Invalid task_id format |

---

### PUT /api/{user_id}/tasks/{task_id}

Update a task's title and/or description.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |
| `task_id` | UUID | Yes | ID of the task |

**Request Body:**
```json
{
  "title": "string | undefined",
  "description": "string | null | undefined"
}
```

**Validation Rules:**
| Field | Rule |
|-------|------|
| `title` | If provided: 1-255 characters, trimmed |
| `description` | If provided: max 2000 characters, null to clear |

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Updated title",
  "description": "Updated description",
  "completed": false,
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T11:00:00Z"
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |
| 404 | Task not found or belongs to another user |
| 422 | Validation failed or invalid task_id format |

---

### DELETE /api/{user_id}/tasks/{task_id}

Permanently delete a task.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |
| `task_id` | UUID | Yes | ID of the task |

**Response: 204 No Content**

*No response body*

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |
| 404 | Task not found or belongs to another user |
| 422 | Invalid task_id format |

---

### PATCH /api/{user_id}/tasks/{task_id}/complete

Toggle task completion status.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | ID of the authenticated user |
| `task_id` | UUID | Yes | ID of the task |

**Request Body:**

*No request body required* (toggles current state)

**Response: 200 OK**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Complete project documentation",
  "description": "Write API docs and user guide",
  "completed": true,
  "created_at": "2025-12-10T10:30:00Z",
  "updated_at": "2025-12-10T11:30:00Z"
}
```

**Errors:**
| Status | Condition |
|--------|-----------|
| 401 | Invalid or missing JWT |
| 403 | URL user_id doesn't match JWT |
| 404 | Task not found or belongs to another user |
| 422 | Invalid task_id format |

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "errors": [
    {
      "field": "title",
      "message": "Title is required"
    }
  ]
}
```

### Standard Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Authentication required |
| `TOKEN_EXPIRED` | 401 | JWT has expired |
| `FORBIDDEN` | 403 | Access denied |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

| Endpoint Pattern | Limit | Window |
|-----------------|-------|--------|
| `POST /api/*/tasks` | 100 | 1 hour |
| `GET /api/*/tasks*` | 1000 | 1 hour |
| `PUT/PATCH/DELETE` | 500 | 1 hour |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702209600
```

---

## CORS Configuration

**Allowed Origins:**
- `https://todoapp.com`
- `http://localhost:3000` (development)

**Allowed Methods:**
- GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers:**
- Authorization, Content-Type

---

## Related Specifications

- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/features/authentication.md` - Authentication feature specification
- `/specs/database/schema.md` - Database schema definitions

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
