# Skill Specification: Create Task

> **Skill ID:** SKILL-CREATE-TASK-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Atomic skill for creating a new task in the database. This skill handles validation, data transformation, and persistence. Used by both Phase 2 (web backend) and Phase 3 (chatbot via MCP).

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
  user_id: string;           // UUID of authenticated user
  title: string;             // Task title (1-255 chars, trimmed)
  description?: string;      // Optional description (0-2000 chars)
  priority?: "low" | "medium" | "high";  // Default: "medium"
  due_date?: string;         // Optional ISO 8601 date
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `user_id` | Required, valid UUID | "User ID is required" | - |
| `title` | Required | "Title is required" | - |
| `title` | Min 1 char (after trim) | "Title cannot be blank" | - |
| `title` | Max 255 chars | "Title must be 255 characters or less" | - |
| `description` | Max 2000 chars | "Description must be 2000 characters or less" | null |
| `priority` | Valid enum | "Priority must be low, medium, or high" | "medium" |
| `due_date` | Valid ISO 8601 | "Due date must be in ISO 8601 format" | null |

---

## Output Schema

```typescript
interface CreateTaskOutput {
  success: boolean;
  task?: {
    id: string;              // UUID
    user_id: string;         // UUID
    title: string;
    description: string | null;
    status: "pending" | "completed";
    priority: "low" | "medium" | "high";
    due_date: string | null; // ISO 8601
    created_at: string;      // ISO 8601
    updated_at: string;      // ISO 8601
  };
  error?: {
    code: string;            // Error code
    message: string;         // Human-readable message
    field?: string;          // Optional field reference
  };
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `UNAUTHORIZED` | Invalid or missing user context |
| `DATABASE_ERROR` | Database operation failed |
| `DUPLICATE_TASK` | Task with same title already exists |

---

## Implementation

### Python (FastAPI/SQLModel)

```python
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlmodel import Session
from models import Task
from pydantic import BaseModel

class CreateTaskInput(BaseModel):
    user_id: str
    title: str
    description: str | None = None
    priority: str = "medium"
    due_date: str | None = None

class CreateTaskOutput(BaseModel):
    success: bool
    task: dict | None = None
    error: dict | None = None

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
            priority=input.priority or "medium",
            due_date=input.due_date,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        # Persist to database
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return CreateTaskOutput(
            success=True,
            task=task.model_dump(mode="json")
        )

    def _validate(self, input: CreateTaskInput) -> dict | None:
        """Validate input and return error if invalid."""

        if not input.user_id:
            return {
                "code": "UNAUTHORIZED",
                "message": "User ID is required",
                "field": "user_id"
            }

        if not input.title or not input.title.strip():
            return {
                "code": "VALIDATION_ERROR",
                "message": "Title is required",
                "field": "title"
            }

        if len(input.title.strip()) > 255:
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

        valid_priorities = ["low", "medium", "high"]
        if input.priority and input.priority not in valid_priorities:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Priority must be low, medium, or high",
                "field": "priority"
            }

        return None
```

### Phase 3 MCP Tool Wrapper

```python
# MCP tool that wraps this skill for Phase 3
async def create_todo(
    user_id: int,
    title: str,
    description: str = None,
    priority: str = "medium",
    due_date: str = None
) -> dict:
    """MCP tool wrapper for create-task skill."""

    # Validate
    if not title or not title.strip():
        return {
            "success": False,
            "error": "Title cannot be empty",
            "code": "VALIDATION_ERROR"
        }

    # Call Phase 2 API
    response = await http_client.post(
        f"{PHASE2_API_URL}/todos",
        json={
            "user_id": user_id,
            "title": title.strip(),
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "status": "pending"
        },
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
    )

    if response.status_code == 201:
        return {
            "success": True,
            "todo": response.json(),
            "message": f"Created task: {title}"
        }
    else:
        return {
            "success": False,
            "error": "Failed to create task",
            "code": "BACKEND_ERROR"
        }
```

---

## Behavior

### Success Flow

```
1. Receive input with user_id, title, and optional fields
2. Validate all input fields against rules
3. Trim whitespace from title
4. Generate UUID for task ID
5. Set completed = false as default
6. Set priority = "medium" if not specified
7. Set created_at and updated_at to current UTC time
8. Insert record into database
9. Return success with task object
```

### Error Flow

```
1. Validation failure → Return error without database operation
2. Database error → Rollback transaction, return error
3. Constraint violation → Return appropriate error
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database INSERT | New row in `tasks` table |
| Timestamp | `created_at` and `updated_at` set to current time |
| Auto-increment | May affect sequence/identity |

---

## Idempotency

**This skill is NOT idempotent.** Each invocation creates a new task with a unique ID. Duplicate calls with identical input create duplicate tasks.

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used directly by FastAPI endpoint `POST /api/{user_id}/tasks`
- Receives JWT-authenticated user_id from path parameter

### Phase 3 (Chatbot)

- Wrapped as MCP tool `create_todo`
- Called by AI agent when user says "Add task..."
- Receives user_id from conversation context

### Reused Components

- Validation logic (shared between phases)
- Error response format (standardized)
- Task model schema (single source of truth)

---

## Testing

### Unit Tests

```python
def test_create_task_success():
    """Task is created with valid input."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title="Test task",
        description="Test description",
        priority="high"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task.title == "Test task"
    assert result.task.priority == "high"
    assert result.task.status == "pending"

def test_create_task_title_required():
    """Error when title is missing."""
    input = CreateTaskInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        title=""
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
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

### Integration Tests

```python
@pytest.mark.asyncio
async def test_create_task_via_api():
    """Test task creation via REST API."""
    client = AsyncClient(app)
    response = await client.post(
        "/api/users/123/tasks",
        json={"title": "API test task"},
        headers={"Authorization": "Bearer valid_jwt"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API test task"
    assert data["status"] == "pending"
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
