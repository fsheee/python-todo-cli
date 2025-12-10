# Skill Specification: Toggle Complete

> **Skill ID:** SKILL-TOGGLE-COMPLETE-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for toggling the completion status of a task. Flips the `completed` boolean from true to false or vice versa.

---

## Skill Configuration

```yaml
skill:
  id: toggle-complete
  name: Toggle Complete
  version: 1.0.0
  description: Toggle task completion status

  type: atomic
  category: status

  requires:
    - database_session
    - user_context
    - task_context
```

---

## Input Schema

```typescript
interface ToggleCompleteInput {
  user_id: string;  // UUID of authenticated user
  task_id: string;  // UUID of task to toggle
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
interface ToggleCompleteOutput {
  success: boolean;
  task?: {
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    completed: boolean;      // New completion status
    created_at: string;
    updated_at: string;      // Updated to current time
  };
  previous_status?: boolean; // Status before toggle
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
from datetime import datetime
from sqlmodel import Session, select
from models import Task
from schemas import ToggleCompleteInput, ToggleCompleteOutput

class ToggleCompleteSkill:
    """Skill for toggling task completion status."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: ToggleCompleteInput) -> ToggleCompleteOutput:
        """Execute the toggle complete skill."""

        # Find task
        task = self.db.exec(
            select(Task).where(Task.id == UUID(input.task_id))
        ).first()

        # Check existence
        if not task:
            return ToggleCompleteOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Check ownership
        if task.user_id != UUID(input.user_id):
            return ToggleCompleteOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Store previous status
        previous_status = task.completed

        # Toggle completion
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return ToggleCompleteOutput(
            success=True,
            task=task.dict(),
            previous_status=previous_status
        )
```

---

## Behavior

### Success Flow
1. Receive input with user_id and task_id
2. Query database for task by ID
3. Verify task exists
4. Verify user owns task
5. Record current completion status
6. Flip `completed` boolean
7. Update `updated_at` timestamp
8. Persist changes
9. Return updated task with previous status

### Toggle Logic
| Current Status | New Status |
|----------------|------------|
| `false` | `true` |
| `true` | `false` |

### Security
- Returns 404 for non-existent tasks
- Returns 404 for tasks owned by other users

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database UPDATE | `completed` field toggled |
| Timestamp | `updated_at` set to current time |

---

## Idempotency

This skill is **NOT idempotent**. Each call toggles the status:
- Call 1: false → true
- Call 2: true → false
- Call 3: false → true

For idempotent behavior, use explicit `set_complete` / `set_incomplete` skills.

---

## Events Emitted

| Event | Condition | Payload |
|-------|-----------|---------|
| `task.completed` | Status changed to true | Task object |
| `task.uncompleted` | Status changed to false | Task object |

---

## Testing

### Unit Tests

```python
def test_toggle_incomplete_to_complete():
    """Toggles incomplete task to complete."""
    task.completed = False
    db.commit()

    result = skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.success is True
    assert result.task.completed is True
    assert result.previous_status is False

def test_toggle_complete_to_incomplete():
    """Toggles complete task to incomplete."""
    task.completed = True
    db.commit()

    result = skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.success is True
    assert result.task.completed is False
    assert result.previous_status is True

def test_toggle_updates_timestamp():
    """updated_at is refreshed on toggle."""
    original_updated_at = task.updated_at

    result = skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.task.updated_at > original_updated_at

def test_toggle_not_found():
    """Returns 404 when task doesn't exist."""
    result = skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=nonexistent_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_toggle_wrong_user():
    """Returns 404 when task belongs to another user."""
    result = skill.execute(ToggleCompleteInput(
        user_id=other_user_id,
        task_id=task_id
    ))

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_double_toggle_returns_to_original():
    """Double toggle returns to original status."""
    original_status = task.completed

    skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=task_id
    ))
    result = skill.execute(ToggleCompleteInput(
        user_id=user_id,
        task_id=task_id
    ))

    assert result.task.completed == original_status
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
