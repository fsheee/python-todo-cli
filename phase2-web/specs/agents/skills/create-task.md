# Skill Specification: Create Task

> **Skill ID:** SKILL-CREATE-TASK-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for creating a new task in the database. This skill handles validation, data transformation, and persistence.

---

## Skill Configuration

```yaml
skill:
  id: create-task
  name: Create Task
  version: 1.0.0
  description: Create a new task for authenticated user

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
interface CreateTaskInput {
  user_id: string;      // UUID of authenticated user
  title: string;        // Task title (1-255 chars)
  description?: string; // Optional description (0-2000 chars)
}
```

### Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| `user_id` | Required, valid UUID | "User ID is required" |
| `title` | Required | "Title is required" |
| `title` | Min 1 char (after trim) | "Title cannot be blank" |
| `title` | Max 255 chars | "Title must be 255 characters or less" |
| `description` | Max 2000 chars | "Description must be 2000 characters or less" |

---

## Output Schema

```typescript
interface CreateTaskOutput {
  success: boolean;
  task?: {
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    completed: boolean;
    created_at: string;  // ISO 8601
    updated_at: string;  // ISO 8601
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
from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import Session
from models import Task
from schemas import CreateTaskInput, CreateTaskOutput

class CreateTaskSkill:
    """Skill for creating a new task."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: CreateTaskInput) -> CreateTaskOutput:
        """Execute the create task skill."""

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return CreateTaskOutput(
                success=False,
                error=validation_error
            )

        # Create task
        task = Task(
            id=uuid4(),
            user_id=UUID(input.user_id),
            title=input.title.strip(),
            description=input.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Persist to database
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return CreateTaskOutput(
            success=True,
            task=task.dict()
        )

    def _validate(self, input: CreateTaskInput) -> dict | None:
        """Validate input and return error if invalid."""

        if not input.title or not input.title.strip():
            return {
                "code": "VALIDATION_ERROR",
                "message": "Title is required",
                "field": "title"
            }

        if len(input.title) > 255:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Title must be 255 characters or less",
                "field": "title"
            }

        if input.description and len(input.description) > 2000:
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
1. Receive input with user_id, title, and optional description
2. Validate all input fields
3. Trim whitespace from title
4. Generate UUID for task ID
5. Set `completed = false` as default
6. Set `created_at` and `updated_at` to current UTC time
7. Insert record into database
8. Return success with task object

### Error Flow
1. Validation failure → Return error without database operation
2. Database error → Rollback transaction, return error
3. Constraint violation → Return appropriate error

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database INSERT | New row in `tasks` table |
| Timestamp | `created_at` and `updated_at` set to current time |

---

## Idempotency

This skill is **NOT idempotent**. Each invocation creates a new task with a unique ID. Duplicate calls create duplicate tasks.

---

## Testing

### Unit Tests

```python
def test_create_task_success():
    """Task is created with valid input."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title="Test task",
        description="Test description"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task.title == "Test task"
    assert result.task.completed is False

def test_create_task_title_required():
    """Error when title is missing."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title=""
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.field == "title"

def test_create_task_title_trimmed():
    """Title whitespace is trimmed."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title="  Test task  "
    )
    result = skill.execute(input)

    assert result.task.title == "Test task"

def test_create_task_title_max_length():
    """Error when title exceeds 255 chars."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title="x" * 256
    )
    result = skill.execute(input)

    assert result.success is False
    assert "255" in result.error.message
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
