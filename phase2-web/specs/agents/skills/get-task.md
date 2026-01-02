# Skill Specification: Get Task

> **Skill ID:** SKILL-GET-TASK-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for retrieving a single task by ID. Used for viewing task details and verifying task ownership before other operations.

---

## Skill Configuration

```yaml
skill:
  id: get-task
  name: Get Task
  version: 1.0.0
  description: Retrieve a single task by ID

  type: atomic
  category: query

  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface GetTaskInput {
  user_id: string;  // UUID of authenticated user
  task_id: string;  // UUID of task to retrieve
}
```

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `user_id` | Required, valid UUID | "User ID is required" |
| `task_id` | Required, valid UUID | "Task ID is required" |

---

## Output Schema

```typescript
interface GetTaskOutput {
  success: boolean;
  task?: {
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    completed: boolean;
    created_at: string;
    updated_at: string;
  };
  error?: {
    code: string;
    message: string;
  };
}
```

---

## Implementation

### Python (FastAPI/SQLModel)

```python
from uuid import UUID
from sqlmodel import Session, select
from models import Task
from schemas import GetTaskInput, GetTaskOutput

class GetTaskSkill:
    """Skill for retrieving a single task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: GetTaskInput) -> GetTaskOutput:
        """Execute the get task skill."""

        # Validate UUID format
        try:
            task_uuid = UUID(input.task_id)
            user_uuid = UUID(input.user_id)
        except ValueError:
            return GetTaskOutput(
                success=False,
                error={
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid ID format"
                }
            )

        # Query task
        task = self.db.exec(
            select(Task).where(Task.id == task_uuid)
        ).first()

        # Check existence
        if not task:
            return GetTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Check ownership (return same error to prevent enumeration)
        if task.user_id != user_uuid:
            return GetTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        return GetTaskOutput(
            success=True,
            task=task.dict()
        )
```

---

## Behavior

### Success Flow
1. Receive input with user_id and task_id
2. Validate UUID formats
3. Query database for task by ID
4. Verify task exists
5. Verify user owns task
6. Return task object

### Security
- Returns 404 for non-existent tasks
- Returns 404 for tasks owned by other users (prevents enumeration)
- No information leakage about existence of other users' tasks

---

## Side Effects

None. This is a read-only operation.

---

## Idempotency

This skill is **idempotent**. Repeated calls with the same input return the same result (assuming no concurrent modifications).

---

## Testing

### Unit Tests

```python
def test_get_task_success():
    """Returns task when it exists and belongs to user."""
    result = skill.execute(GetTaskInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.success is True
    assert result.task.id == str(task_id)
    assert result.task.user_id == str(user_id)

def test_get_task_includes_all_fields():
    """Response includes all task fields."""
    result = skill.execute(GetTaskInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert "id" in result.task
    assert "user_id" in result.task
    assert "title" in result.task
    assert "description" in result.task
    assert "completed" in result.task
    assert "created_at" in result.task
    assert "updated_at" in result.task

def test_get_task_not_found():
    """Returns 404 when task doesn't exist."""
    result = skill.execute(GetTaskInput(
        user_id=user_id,
        task_id=nonexistent_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_get_task_wrong_user():
    """Returns 404 when task belongs to another user."""
    result = skill.execute(GetTaskInput(
        user_id=other_user_id,
        task_id=task_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_get_task_invalid_uuid():
    """Returns validation error for invalid UUID."""
    result = skill.execute(GetTaskInput(
        user_id=user_id,
        task_id="not-a-uuid"
    ))

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
```

---

## Related Specifications

- `/specs/features/task-crud.md` - Task CRUD feature specification
- `/specs/agents/todo-agent.md` - Parent agent
- `/specs/database/schema.md` - Database schema

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
