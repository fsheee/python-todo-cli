# Skill Specification: Delete Task

> **Skill ID:** SKILL-DELETE-TASK-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for permanently deleting a task from the database. This is a destructive operation with no undo capability.

---

## Skill Configuration

```yaml
skill:
  id: delete-task
  name: Delete Task
  version: 1.0.0
  description: Permanently delete a task

  type: atomic
  category: crud
  destructive: true

  requires:
    - database_session
    - user_context
    - task_context
```

---

## Input Schema

```typescript
interface DeleteTaskInput {
  user_id: string;  // UUID of authenticated user
  task_id: string;  // UUID of task to delete
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
interface DeleteTaskOutput {
  success: boolean;
  deleted_id?: string;  // ID of deleted task
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
from schemas import DeleteTaskInput, DeleteTaskOutput

class DeleteTaskSkill:
    """Skill for deleting a task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: DeleteTaskInput) -> DeleteTaskOutput:
        """Execute the delete task skill."""

        # Find task
        task = self.db.exec(
            select(Task).where(Task.id == UUID(input.task_id))
        ).first()

        # Check existence
        if not task:
            return DeleteTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Check ownership
        if task.user_id != UUID(input.user_id):
            return DeleteTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"  # Don't leak existence
                }
            )

        # Store ID for response
        deleted_id = str(task.id)

        # Delete from database
        self.db.delete(task)
        self.db.commit()

        return DeleteTaskOutput(
            success=True,
            deleted_id=deleted_id
        )
```

---

## Behavior

### Success Flow
1. Receive input with user_id and task_id
2. Query database for task by ID
3. Verify task exists
4. Verify user owns task
5. Delete task from database
6. Return success with deleted task ID

### Security
- Returns 404 for non-existent tasks
- Returns 404 for tasks owned by other users (no information leakage)
- Hard delete (no soft delete/archive)

### Deletion Behavior
- Task is permanently removed
- No cascade effects (tasks have no child records)
- Operation cannot be undone

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database DELETE | Row removed from `tasks` table |

---

## Idempotency

This skill is **NOT idempotent**.
- First call: Deletes task, returns success
- Subsequent calls: Returns NOT_FOUND error

---

## Testing

### Unit Tests

```python
def test_delete_task_success():
    """Task is deleted successfully."""
    result = skill.execute(DeleteTaskInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.success is True
    assert result.deleted_id == str(task_id)

    # Verify task no longer exists
    task = db.get(Task, task_id)
    assert task is None

def test_delete_task_not_found():
    """Returns 404 when task doesn't exist."""
    result = skill.execute(DeleteTaskInput(
        user_id=user_id,
        task_id=nonexistent_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_delete_task_wrong_user():
    """Returns 404 when task belongs to another user."""
    result = skill.execute(DeleteTaskInput(
        user_id=other_user_id,
        task_id=task_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_delete_task_already_deleted():
    """Returns 404 when deleting same task twice."""
    # First delete succeeds
    skill.execute(DeleteTaskInput(
        user_id=user_id,
        task_id=task_id
    ))

    # Second delete fails
    result = skill.execute(DeleteTaskInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"
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
