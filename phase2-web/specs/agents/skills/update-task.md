# Skill Specification: Update Task

> **Skill ID:** SKILL-UPDATE-TASK-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for updating an existing task's title and/or description. Supports partial updates where only provided fields are modified.

---

## Skill Configuration

```yaml
skill:
  id: update-task
  name: Update Task
  version: 1.0.0
  description: Update task title and/or description

  type: atomic
  category: crud

  requires:
    - database_session
    - user_context
    - task_context
```

---

## Input Schema

```typescript
interface UpdateTaskInput {
  user_id: string;         // UUID of authenticated user
  task_id: string;         // UUID of task to update
  title?: string;          // New title (1-255 chars if provided)
  description?: string | null;  // New description (null to clear)
}
```

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `user_id` | Required, valid UUID | "User ID is required" |
| `task_id` | Required, valid UUID | "Task ID is required" |
| `title` | If provided: min 1 char (after trim) | "Title cannot be blank" |
| `title` | If provided: max 255 chars | "Title must be 255 characters or less" |
| `description` | If provided: max 2000 chars or null | "Description must be 2000 characters or less" |

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
    completed: boolean;
    created_at: string;
    updated_at: string;  // Updated to current time
  };
  error?: {
    code: string;
    message: string;
    field?: string;
  };
}
```

---

## Implementation

### Python (FastAPI/SQLModel)

```python
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
from models import Task
from schemas import UpdateTaskInput, UpdateTaskOutput

class UpdateTaskSkill:
    """Skill for updating an existing task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: UpdateTaskInput) -> UpdateTaskOutput:
        """Execute the update task skill."""

        # Find task
        task = self.db.exec(
            select(Task).where(Task.id == UUID(input.task_id))
        ).first()

        # Check existence
        if not task:
            return UpdateTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Check ownership
        if task.user_id != UUID(input.user_id):
            return UpdateTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"  # Don't leak existence
                }
            )

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return UpdateTaskOutput(
                success=False,
                error=validation_error
            )

        # Apply updates
        if input.title is not None:
            task.title = input.title.strip()

        if "description" in input.__fields_set__:
            task.description = input.description

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return UpdateTaskOutput(
            success=True,
            task=task.dict()
        )

    def _validate(self, input: UpdateTaskInput) -> dict | None:
        """Validate input fields."""

        if input.title is not None:
            if not input.title.strip():
                return {
                    "code": "VALIDATION_ERROR",
                    "message": "Title cannot be blank",
                    "field": "title"
                }
            if len(input.title) > 255:
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

        return None
```

---

## Behavior

### Success Flow
1. Receive input with user_id, task_id, and fields to update
2. Query database for task by ID
3. Verify task exists
4. Verify user owns task
5. Validate provided fields
6. Apply updates to provided fields only
7. Update `updated_at` timestamp
8. Persist changes
9. Return updated task

### Partial Update
- Only fields explicitly provided are updated
- Omitted fields retain their current values
- `description: null` clears the description
- `description` omitted leaves description unchanged

### Security
- Returns 404 for non-existent tasks
- Returns 404 for tasks owned by other users (no information leakage)
- Cannot update `id`, `user_id`, `created_at`, or `completed`

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database UPDATE | Modified row in `tasks` table |
| Timestamp | `updated_at` set to current time |

---

## Idempotency

This skill is **idempotent** for the same input values. Repeated calls with the same data produce the same result (though `updated_at` changes).

---

## Testing

### Unit Tests

```python
def test_update_task_title_only():
    """Updates title when only title provided."""
    original_desc = task.description
    result = skill.execute(UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        title="New title"
    ))

    assert result.success is True
    assert result.task.title == "New title"
    assert result.task.description == original_desc

def test_update_task_description_only():
    """Updates description when only description provided."""
    original_title = task.title
    result = skill.execute(UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        description="New description"
    ))

    assert result.success is True
    assert result.task.title == original_title
    assert result.task.description == "New description"

def test_update_task_clear_description():
    """Clears description when null provided."""
    result = skill.execute(UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        description=None
    ))

    assert result.success is True
    assert result.task.description is None

def test_update_task_not_found():
    """Returns 404 when task doesn't exist."""
    result = skill.execute(UpdateTaskInput(
        user_id=user_id,
        task_id=nonexistent_id,
        title="New title"
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_update_task_wrong_user():
    """Returns 404 when task belongs to another user."""
    result = skill.execute(UpdateTaskInput(
        user_id=other_user_id,
        task_id=task_id,
        title="New title"
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_update_task_updates_timestamp():
    """updated_at is refreshed on update."""
    original_updated_at = task.updated_at
    result = skill.execute(UpdateTaskInput(
        user_id=user_id,
        task_id=task_id,
        title="New title"
    ))

    assert result.task.updated_at > original_updated_at
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
