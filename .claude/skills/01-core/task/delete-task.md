# Skill Specification: Delete Task

> **Skill ID:** SKILL-DELETE-TASK-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Atomic skill for deleting a task. This skill permanently removes a task from the database. Requires explicit confirmation for destructive operations. Only the owner can delete their tasks.

---

## Skill Configuration

```yaml
skill:
  id: delete-task
  name: Delete Task
  version: 1.0.0
  description: Delete a task (requires explicit confirmation)

  # Skill type
  type: atomic
  category: crud

  # Destructive flag
  destructive: true

  # Dependencies
  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface DeleteTaskInput {
  user_id: string;           // UUID of authenticated user
  task_id: string;           // UUID of task to delete
  confirm: boolean;          // Explicit confirmation required (true)
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `user_id` | Required, valid UUID | "User ID is required" | - |
| `task_id` | Required, valid UUID | "Task ID is required" | - |
| `confirm` | Required, must be true | "Deletion requires explicit confirmation" | - |

---

## Output Schema

```typescript
interface DeleteTaskOutput {
  success: boolean;
  deleted_task_id?: string;  // UUID of deleted task
  message?: string;          // Human-readable result message
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
| `VALIDATION_ERROR` | Input validation failed or confirmation missing |
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

class DeleteTaskInput(BaseModel):
    user_id: str
    task_id: str
    confirm: bool = False

class DeleteTaskOutput(BaseModel):
    success: bool
    deleted_task_id: str | None = None
    message: str | None = None
    error: dict | None = None

class DeleteTaskSkill:
    """Skill for deleting a task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: DeleteTaskInput) -> DeleteTaskOutput:
        """Execute the delete task skill."""

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return DeleteTaskOutput(
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
            return DeleteTaskOutput(
                success=False,
                error={
                    "code": "NOT_FOUND",
                    "message": "Task not found"
                }
            )

        # Store task info before deletion
        deleted_task_id = str(task.id)
        task_title = task.title

        # Delete task
        self.db.delete(task)
        self.db.commit()

        return DeleteTaskOutput(
            success=True,
            deleted_task_id=deleted_task_id,
            message=f'Deleted task: "{task_title}"'
        )

    def _validate(self, input: DeleteTaskInput) -> dict | None:
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

        if not input.confirm:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Deletion requires explicit confirmation. Set confirm=true",
                "field": "confirm"
            }

        return None
```

### Phase 3 MCP Tool Wrapper

```python
async def delete_todo(
    user_id: int,
    task_id: int,
    confirm: bool = True
) -> dict:
    """MCP tool wrapper for delete-task skill."""

    if not confirm:
        # Get task info for confirmation message
        task_response = await http_client.get(
            f"{PHASE2_API_URL}/todos/{task_id}",
            headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
        )

        if task_response.status_code == 200:
            task = task_response.json()
            return {
                "success": False,
                "needs_confirmation": True,
                "message": f'Are you sure you want to delete "{task.get("title")}"?',
                "task_id": task_id
            }
        else:
            return {
                "success": False,
                "error": "Task not found",
                "code": "NOT_FOUND"
            }

    response = await http_client.delete(
        f"{PHASE2_API_URL}/todos/{task_id}",
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
    )

    if response.status_code == 200:
        return {
            "success": True,
            "message": "Task deleted successfully"
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
            "error": "Failed to delete task",
            "code": "BACKEND_ERROR"
        }
```

---

## Behavior

### Success Flow

```
1. Receive input with user_id, task_id, and confirm=true
2. Validate all input fields
3. Find task by ID and verify ownership
4. Store task info for response message
5. Delete task from database
6. Return success with deleted task ID
```

### Error Flow

```
1. Validation failure (missing confirm) → Return error with confirmation request
2. Validation failure (missing IDs) → Return validation error
3. Task not found → Return NOT_FOUND error
4. Database error → Return error with code
```

### Confirmation Flow (Phase 3)

```
1. User requests deletion without confirm
2. Skill returns needs_confirmation=true with task info
3. AI agent asks user for confirmation
4. User confirms with "yes"
5. Skill deletes task on second call with confirm=true
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database DELETE | Removes row from tasks table |
| Cascade | Related data may be affected |
| Irreversible | Cannot undo deletion |

---

## Idempotency

**This skill is idempotent for the confirmation check.** If task is already deleted, returns NOT_FOUND on first attempt (not an error after deletion).

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used directly by FastAPI endpoint `DELETE /api/{user_id}/tasks/{task_id}`
- Requires user confirmation in UI before calling

### Phase 3 (Chatbot)

- Wrapped as MCP tool `delete_todo`
- Supports implicit confirmation flow
- Returns needs_confirmation flag for UI

### Reused Components

- Ownership verification (consistent)
- Confirmation logic (shared pattern)
- Response format (standardized)

---

## Testing

### Unit Tests

```python
def test_delete_task_success():
    """Task is deleted with valid input and confirmation."""
    input = DeleteTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        confirm=True
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.deleted_task_id == input.task_id

def test_delete_task_not_confirmed():
    """Error when confirmation is missing."""
    input = DeleteTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        confirm=False
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
    assert "confirmation" in result.error.message

def test_delete_task_not_found():
    """Error when task not found."""
    input = DeleteTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440999",
        confirm=True
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "NOT_FOUND"

def test_delete_task_already_deleted():
    """Error when task already deleted (idempotent check)."""
    # First delete succeeds
    input = DeleteTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        task_id="550e8400-e29b-41d4-a716-446655440002",
        confirm=True
    )
    result = skill.execute(input)

    # Second delete returns NOT_FOUND
    result2 = skill.execute(input)
    assert result2.success is False
    assert result2.error.code == "NOT_FOUND"
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
| 1.0.0 | 2025-12-31 | Claude | Updated with Phase 3 MCP wrapper and confirmation flow |
