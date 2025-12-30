# Skill Specification: List Tasks

> **Skill ID:** SKILL-LIST-TASKS-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Atomic skill for retrieving tasks with optional filtering. This skill supports filtering by status, priority, and pagination. Used by both Phase 2 (web backend) and Phase 3 (chatbot via MCP).

---

## Skill Configuration

```yaml
skill:
  id: list-tasks
  name: List Tasks
  version: 1.0.0
  description: Retrieve tasks with optional filtering by status and priority

  # Skill type
  type: atomic
  category: query

  # Dependencies
  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface ListTasksInput {
  user_id: string;                    // UUID of authenticated user
  status?: "pending" | "completed" | "all";  // Filter by status (default: "all")
  priority?: "low" | "medium" | "high";      // Filter by priority (optional)
  limit?: number;                     // Max results (1-100, default: 20)
  offset?: number;                    // Pagination offset (default: 0)
  sort_by?: "created_at" | "updated_at" | "priority" | "title";
  sort_order?: "asc" | "desc";        // Sort order (default: "desc")
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `user_id` | Required, valid UUID | "User ID is required" | - |
| `status` | Valid enum | "Status must be pending, completed, or all" | "all" |
| `priority` | Valid enum | "Priority must be low, medium, or high" | null |
| `limit` | Min 1, Max 100 | "Limit must be between 1 and 100" | 20 |
| `offset` | Min 0 | "Offset must be 0 or greater" | 0 |

---

## Output Schema

```typescript
interface ListTasksOutput {
  success: boolean;
  tasks?: Array<{
    id: string;              // UUID
    user_id: string;         // UUID
    title: string;
    description: string | null;
    status: "pending" | "completed";
    priority: "low" | "medium" | "high";
    due_date: string | null; // ISO 8601
    created_at: string;      // ISO 8601
    updated_at: string;      // ISO 8601
  }>;
  count?: number;            // Number of tasks returned
  total?: number;            // Total tasks matching filter
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
| `UNAUTHORIZED` | Invalid or missing user context |
| `DATABASE_ERROR` | Database operation failed |

---

## Implementation

### Python (FastAPI/SQLModel)

```python
from sqlalchemy import select, func
from sqlmodel import Session, select
from models import Task
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ListTasksInput(BaseModel):
    user_id: str
    status: str = "all"
    priority: Optional[str] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"

class ListTasksOutput(BaseModel):
    success: bool
    tasks: list | None = None
    count: int | None = None
    total: int | None = None
    error: dict | None = None

class ListTasksSkill:
    """Skill for listing tasks with filtering."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: ListTasksInput) -> ListTasksOutput:
        """Execute the list tasks skill."""

        # Validate input
        validation_error = self._validate(input)
        if validation_error:
            return ListTasksOutput(
                success=False,
                error=validation_error
            )

        # Build query
        query = select(Task).where(Task.user_id == UUID(input.user_id))

        # Apply status filter
        if input.status and input.status != "all":
            completed = input.status == "completed"
            query = query.where(Task.completed == completed)

        # Apply priority filter
        if input.priority:
            query = query.where(Task.priority == input.priority)

        # Get total count
        total_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(total_query).scalar() or 0

        # Apply sorting
        sort_column = getattr(Task, input.sort_by, Task.created_at)
        if input.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(input.offset).limit(input.limit)

        # Execute query
        tasks = self.db.execute(query).scalars().all()

        return ListTasksOutput(
            success=True,
            tasks=[task.model_dump(mode="json") for task in tasks],
            count=len(tasks),
            total=total
        )

    def _validate(self, input: ListTasksInput) -> dict | None:
        """Validate input and return error if invalid."""

        valid_statuses = ["pending", "completed", "all"]
        if input.status not in valid_statuses:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Status must be pending, completed, or all",
                "field": "status"
            }

        valid_priorities = ["low", "medium", "high"]
        if input.priority and input.priority not in valid_priorities:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Priority must be low, medium, or high",
                "field": "priority"
            }

        if input.limit < 1 or input.limit > 100:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Limit must be between 1 and 100",
                "field": "limit"
            }

        if input.offset < 0:
            return {
                "code": "VALIDATION_ERROR",
                "message": "Offset must be 0 or greater",
                "field": "offset"
            }

        return None
```

### Phase 3 MCP Tool Wrapper

```python
async def list_todos(
    user_id: int,
    status: str = "all",
    priority: str = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """MCP tool wrapper for list-tasks skill."""

    response = await http_client.get(
        f"{PHASE2_API_URL}/todos",
        params={
            "user_id": user_id,
            "status": status,
            "priority": priority,
            "limit": limit,
            "offset": offset
        },
        headers={"Authorization": f"Bearer {SERVICE_TOKEN}"}
    )

    if response.status_code == 200:
        return {
            "success": True,
            "tasks": response.json(),
            "count": len(response.json())
        }
    else:
        return {
            "success": False,
            "error": "Failed to list tasks",
            "code": "BACKEND_ERROR"
        }
```

---

## Behavior

### Success Flow

```
1. Receive input with user_id and optional filters
2. Validate all input fields
3. Build database query with user_id filter
4. Apply status filter if specified
5. Apply priority filter if specified
6. Get total count of matching tasks
7. Apply sorting and pagination
8. Execute query and return tasks
```

### Error Flow

```
1. Validation failure → Return error without database query
2. Database error → Return error with code
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database SELECT | Read operations on tasks table |
| No state change | This skill is read-only |

---

## Idempotency

**This skill is idempotent.** Multiple calls with identical input return the same results (assuming no concurrent modifications).

---

## Reuse Across Phases

### Phase 2 (Web Backend)

- Used directly by FastAPI endpoint `GET /api/{user_id}/tasks`
- Supports all filtering and pagination options

### Phase 3 (Chatbot)

- Wrapped as MCP tool `list_todos`
- Called by AI agent when user says "Show my tasks"
- Simplifies parameters for natural conversation

### Reused Components

- Query building logic (shared between phases)
- Response format (standardized)
- Pagination calculations (consistent)

---

## Testing

### Unit Tests

```python
def test_list_tasks_success():
    """Returns tasks for valid user."""
    input = ListTasksInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        status="all",
        limit=10
    )
    result = skill.execute(input)

    assert result.success is True
    assert isinstance(result.tasks, list)
    assert result.count >= 0

def test_list_tasks_by_status():
    """Filters tasks by status."""
    input = ListTasksInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        status="pending"
    )
    result = skill.execute(input)

    assert result.success is True
    for task in result.tasks:
        assert task.status == "pending"

def test_list_tasks_pagination():
    """Respects pagination parameters."""
    input = ListTasksInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        limit=5,
        offset=10
    )
    result = skill.execute(input)

    assert result.success is True
    assert len(result.tasks) <= 5

def test_list_tasks_invalid_limit():
    """Error when limit is out of range."""
    input = ListTasksInput(
        user_id="550e8400-e29b-41d4-a716-446655440001",
        limit=200
    )
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
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
