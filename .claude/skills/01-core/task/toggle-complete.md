# Skill Specification: Toggle Complete

> **Skill ID:** SKILL-TOGGLE-COMPLETE-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Atomic skill for toggling task completion status. This skill switches a task between pending and completed states. If task is pending, marks as complete; if complete, marks as pending.

---

## Skill Configuration

```yaml
skill:
  id: toggle-complete
  name: Toggle Complete
  version: 1.0.0
  description: Toggle task between pending and completed status

  # Skill type
  type: atomic
  category: status

  # Dependencies
  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface ToggleCompleteInput {
  user_id: string;           // UUID of authenticated user
  task_id: string;           // UUID of task to toggle
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `user_id` | Required, valid UUID | "User ID is required" | - |
| `task_id` | Required, valid UUID | "Task ID is required" | - |

---

## Output Schema

```typescript
interface ToggleCompleteOutput {
  success: boolean;
  task?: {
    id: string;
    user_id: string;
    title: string;
    status: "pending" | "completed";
    completed: boolean;
    updated_at: string;
  };
  message?: string;          // Human-readable result message
  error?: {
    code: string;
    message: string;
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

class ToggleCompleteInput(BaseModel):
    user_id: str
    task_id: str

class ToggleCompleteOutput(BaseModel):
    success: bool
    task: dict | None = None
    message: str | None = None
    error: dict | None = None

class ToggleCompleteSkill:
    """Skill for toggling task completion status."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: ToggleCompleteInput) -> ToggleCompleteOutput:
        """Execute the toggle complete skill."""

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return ToggleCompleteOutput(
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
            return ToggleCompleteOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Toggle completion status
        task.completed = not task.completed
        task.updated_at = datetime.now(timezone.utc)

        # Persist changes
        self.db.commit()
        self.db.refresh(task)

        # Generate message
        status_text = "completed" if task.completed else "pending"
        message = f'Task "{task.title}" is now {status_text}'

        return ToggleCompleteOutput(
            success=True,
            task=task.model_dump(mode="json"),
            message=message
        )

    def _validate(self, input: ToggleCompleteInput) -> dict | None:
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

        return None
```

### Phase 3 MCP Tool Wrapper

```python
async def toggle_complete(
    user_id: int,
    task_id: int
) -> dict:
    """MCP tool wrapper for toggle-complete skill."""

    response = await http_client.put(
        f"{PHASE2_API_URL}/todos/{task_id}/toggle",
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
    )

    if response.status_code == 200:
        task = response.json()
        status = "completed" if task.get("completed") else "pending"
        return {
            "success": True,
            "task": task,
            "message": f'Task "{task.get("title")}" is now {status}'
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
            "error": "Failed to toggle task",
            "code": "BACKEND_ERROR"
        }
```

---

## Behavior

### Success Flow

```
1. Receive input with user_id and task_id
2. Validate input fields
3. Find task and verify ownership
4. Toggle completed boolean
5. Update updated_at timestamp
6. Persist changes
7. Return updated task with status message
```

### Error Flow

```
1. Validation failure → Return error without database query
2. Task not found → Return NOT_FOUND error
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database UPDATE | Modifies completed flag and updated_at |
| No cascade | No related data affected |

---

## Idempotency

**This skill is idempotent.** Calling multiple times alternates between two states: pending → completed → pending → completed.

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used directly by FastAPI endpoint `PUT /api/{user_id}/tasks/{task_id}/toggle`

### Phase 3 (Chatbot)

- Wrapped as MCP tool `toggle_complete`
- Called by AI agent when user says "Complete the first one"
- Simplified interface (only user_id and task_id)

### Reused Components

- Ownership verification (consistent)
- Timestamp update (same as update-task)
- Response format (standardized)

---

## Testing

### Unit Tests

```python
def test_toggle_complete_pending_to_complete():
    """Pending task becomes completed."""
    input = ToggleCompleteInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task.completed is True
    assert result.task.status == "completed"
    assert "completed" in result.message

def test_toggle_complete_complete_to_pending():
    """Completed task becomes pending."""
    # First toggle
    input = ToggleCompleteInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002"
    )
    result1 = skill.execute(input)

    # Second toggle
    result2 = skill.execute(input)

    assert result2.success is True
    assert result2.task.completed is False
    assert result2.task.status == "pending"

def test_toggle_complete_not_found():
    """Error when task not found."""
    input = ToggleCompleteInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440999"
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "NOT_FOUND"
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
