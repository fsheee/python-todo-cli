# Skill Specification: Update Task

> **Skill ID:** SKILL-UPDATE-TASK-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Atomic skill for updating an existing task. This skill allows modifying any task field (title, description, status, priority, due_date). Only the owner can update their tasks.

---

## Skill Configuration

```yaml
skill:
  id: update-task
  name: Update Task
  version: 1.0.0
  description: Update task fields: title, description, status, priority, or due date

  # Skill type
  type: atomic
  category: crud

  # Dependencies
  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface UpdateTaskInput {
  user_id: string;           // UUID of authenticated user
  task_id: string;           // UUID of task to update
  title?: string;            // New title (1-255 chars, optional)
  description?: string;      // New description (0-2000 chars, optional)
  status?: "pending" | "completed";  // New status (optional)
  priority?: "low" | "medium" | "high";  // New priority (optional)
  due_date?: string;         // New due date (ISO 8601, optional)
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `user_id` | Required, valid UUID | "User ID is required" | - |
| `task_id` | Required, valid UUID | "Task ID is required" | - |
| `title` | Min 1 char (after trim) | "Title cannot be blank" | unchanged |
| `title` | Max 255 chars | "Title must be 255 characters or less" | unchanged |
| `description` | Max 2000 chars | "Description must be 2000 characters or less" | unchanged |
| `status` | Valid enum | "Status must be pending or completed" | unchanged |
| `priority` | Valid enum | "Priority must be low, medium, or high" | unchanged |
| `due_date` | Valid ISO 8601 | "Due date must be in ISO 8601 format" | unchanged |

---

## Output Schema

```typescript
interface UpdateTaskOutput {
  success: boolean;
  task?: {
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    status: "pending" | "completed";
    priority: "low" | "medium" | "high";
    due_date: string | null;
    created_at: string;
    updated_at: string;
  };
  error?: {
    code: string;
    message: string;
    field?: string;
  };
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Task not found or doesn't belong to user |
| `UNAUTHORIZED` | Invalid or missing user context |
| `DATABASE_ERROR` | Database operation failed |

---

## Implementation

### Python (FastAPI/SQLModel)

```python
from uuid import UUID
from datetime import datetime, timezone
from sqlmodel import Session, select
from models import Task
from pydantic import BaseModel
from typing import Optional

class UpdateTaskInput(BaseModel):
    user_id: str
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None

class UpdateTaskOutput(BaseModel):
    success: bool
    task: dict | None = None
    error: dict | None = None

class UpdateTaskSkill:
    """Skill for updating an existing task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: UpdateTaskInput) -> UpdateTaskOutput:
        """Execute the update task skill."""

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return UpdateTaskOutput(
                success=False,
                error=validation_error
            )

        # Find task (owned by user)
        task = self.db.exec(
            select(Task).where(
                Task.id == UUID(input.task_id),
                Task.user_id == UUID(input.user_id)
            )
        ).first()

        if not task:
            return UpdateTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Update fields (only provided fields)
        if input.title is not None:
            task.title = input.title.strip()
        if input.description is not None:
            task.description = input.description
        if input.status is not None:
            task.completed = input.status == "completed"
        if input.priority is not None:
            task.priority = input.priority
        if input.due_date is not None:
            task.due_date = input.due_date

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc)

        # Persist changes
        self.db.commit()
        self.db.refresh(task)

        return UpdateTaskOutput(
            success=True,
            task=task.model_dump(mode="json")
        )

    def _validate(self, input: UpdateTaskInput) -> dict | None:
        """Validate input and return error if invalid."""

        if not input.user_id:
            return {
                "code": "UNAUTHORIZED",
                "message": "User ID is required",
                "field": "user_id"
            }

        if not input.task_id:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Task ID is required",
                "field": "task_id"
            }

        if input.title is not None:
            if not input.title.strip():
                return {
                    "code": "VALIDATION_ERROR",
                    "message": "Title cannot be blank",
                    "field": "title"
                }
            if len(input.title.strip()) > 255:
                return {
                    "code": "VALIDATION_ERROR",
                    "message": "Title must be 255 characters or less",
                    "field": "title"
                }

        if input.description is not None and len(input.description) > 2000:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Description must be 2000 characters or less",
                "field": "description"
            }

        valid_statuses = ["pending", "completed"]
        if input.status is not None and input.status not in valid_statuses:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Status must be pending or completed",
                "field": "status"
            }

        valid_priorities = ["low", "medium", "high"]
        if input.priority is not None and input.priority not in valid_priorities:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Priority must be low, medium, or high",
                "field": "priority"
            }

        return None
```

### Phase 3 MCP Tool Wrapper

```python
async def update_todo(
    user_id: int,
    task_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    due_date: str = None
) -> dict:
    """MCP tool wrapper for update-task skill."""

    # Validate at least one field is being updated
    if all(v is None for v in [title, description, status, priority, due_date]):
        return {
            "success": False,
            "error": "At least one field must be provided to update",
            "code": "VALIDATION_ERROR"
        }

    payload = {}
    if title is not None: payload["title"] = title
    if description is not None: payload["description"] = description
    if status is not None: payload["status"] = status
    if priority is not None: payload["priority"] = priority
    if due_date is not None: payload["due_date"] = due_date

    response = await http_client.put(
        f"{PHASE2_API_URL}/todos/{task_id}",
        json=payload,
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
    )

    if response.status_code == 200:
        return {
            "success": True,
            "todo": response.json(),
            "message": f"Updated task: {response.json().get('title')}"
        }
    elif response.status_code == 404:
        return {
            "success": False,
            "error": "Task not found",
            "code": "NOT_FOUND"
        }
    else:
        return {
            "success": False,
            "error": "Failed to update task",
            "code": "BACKEND_ERROR"
        }
```

---

## Behavior

### Success Flow

```
1. Receive input with user_id, task_id, and fields to update
2. Validate all input fields
3. Find task by ID and verify ownership
4. Update only the provided fields
5. Update updated_at timestamp
6. Persist changes to database
7. Return updated task object
```

### Error Flow

```
1. Validation failure → Return error without database query
2. Task not found → Return NOT_FOUND error
3. Task doesn't belong to user → Return NOT_FOUND error
4. Database error → Return error with code
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database UPDATE | Modifies existing row in tasks table |
| Timestamp | `updated_at` set to current time |

---

## Idempotency

**This skill is idempotent.** Repeated calls with identical input produce the same result (after first call, subsequent calls return the same data without changes).

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used directly by FastAPI endpoint `PUT /api/{user_id}/tasks/{task_id}`
- Receives user_id from JWT, task_id from path

### Phase 3 (Chatbot)

- Wrapped as MCP tool `update_todo`
- Called by AI agent when user says "Change priority to high"
- All fields optional (only update what's specified)

### Reused Components

- Validation logic (shared between phases)
- Ownership check (consistent authorization)
- Response format (standardized)

---

## Testing

### Unit Tests

```python
def test_update_task_success():
    """Task is updated with valid input."""
    input = UpdateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        title="Updated title",
        priority="high"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task.title == "Updated title"
    assert result.task.priority == "high"

def test_update_task_not_found():
    """Error when task not found."""
    input = UpdateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440999",
        title="Updated"
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_update_task_partial():
    """Only specified fields are updated."""
    input = UpdateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        status="completed"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task.status == "completed"
    # Other fields remain unchanged

def test_update_task_empty_title():
    """Error when title is empty."""
    input = UpdateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        title="   "
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
    assert result.error.field == "title"
```

---

## Related Specifications

- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/agents/todo-agent.md` - Parent agent
- `/specs/database/schema.md` - Database schema
- `/specs/api/rest-endpoints.md` - REST API endpoints
- `/specs/api/mcp-tools.md` - Phase 3 MCP tool wrapper

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-10 | Claude | Initial specification |
| 1.0.0 | 2025-12-31 | Claude | Updated with Phase 3 MCP wrapper |
