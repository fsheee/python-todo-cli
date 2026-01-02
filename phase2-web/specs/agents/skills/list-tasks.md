# Skill Specification: List Tasks

> **Skill ID:** SKILL-LIST-TASKS-001
> **Version:** 1.0
> **Status:** Draft
> **Last Updated:** 2025-12-10

---

## Overview

Atomic skill for retrieving all tasks belonging to an authenticated user with optional filtering, sorting, and pagination.

---

## Skill Configuration

```yaml
skill:
  id: list-tasks
  name: List Tasks
  version: 1.0.0
  description: Retrieve tasks for authenticated user with filters

  type: atomic
  category: query

  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface ListTasksInput {
  user_id: string;        // UUID of authenticated user
  filters?: {
    completed?: boolean;  // Filter by completion status
  };
  sort?: {
    field: 'created_at' | 'updated_at' | 'title';
    order: 'asc' | 'desc';
  };
  pagination?: {
    limit: number;        // Max 100, default 50
    offset: number;       // Default 0
  };
}
```

### Validation Rules

| Field | Rule | Default |
|-------|------|---------|
| `user_id` | Required, valid UUID | - |
| `sort.field` | One of: created_at, updated_at, title | created_at |
| `sort.order` | One of: asc, desc | desc |
| `pagination.limit` | 1-100 | 50 |
| `pagination.offset` | >= 0 | 0 |

---

## Output Schema

```typescript
interface ListTasksOutput {
  success: boolean;
  tasks?: Array<{
    id: string;
    user_id: string;
    title: string;
    description: string | null;
    completed: boolean;
    created_at: string;
    updated_at: string;
  }>;
  meta?: {
    count: number;    // Number of tasks returned
    total: number;    // Total tasks matching filters
    limit: number;
    offset: number;
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
from sqlmodel import Session, select, func
from models import Task
from schemas import ListTasksInput, ListTasksOutput

class ListTasksSkill:
    """Skill for listing user tasks with filters."""

    def __init__(self, db: Session):
        self.db = db

    async def execute(self, input: ListTasksInput) -> ListTasksOutput:
        """Execute the list tasks skill."""

        # Build base query
        query = select(Task).where(Task.user_id == UUID(input.user_id))
        count_query = select(func.count(Task.id)).where(
            Task.user_id == UUID(input.user_id)
        )

        # Apply filters
        if input.filters and input.filters.completed is not None:
            query = query.where(Task.completed == input.filters.completed)
            count_query = count_query.where(
                Task.completed == input.filters.completed
            )

        # Get total count
        total = self.db.exec(count_query).one()

        # Apply sorting
        sort_field = input.sort.field if input.sort else "created_at"
        sort_order = input.sort.order if input.sort else "desc"

        order_column = getattr(Task, sort_field)
        if sort_order == "desc":
            order_column = order_column.desc()
        query = query.order_by(order_column)

        # Apply pagination
        limit = min(input.pagination.limit if input.pagination else 50, 100)
        offset = input.pagination.offset if input.pagination else 0
        query = query.offset(offset).limit(limit)

        # Execute query
        tasks = self.db.exec(query).all()

        return ListTasksOutput(
            success=True,
            tasks=[task.dict() for task in tasks],
            meta={
                "count": len(tasks),
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )
```

---

## Behavior

### Success Flow
1. Receive input with user_id and optional filters
2. Build query scoped to user_id
3. Apply completion filter if specified
4. Count total matching records
5. Apply sorting (default: created_at desc)
6. Apply pagination (default: limit 50, offset 0)
7. Execute query and return results with metadata

### Empty Results
- Returns empty array `[]` when no tasks match
- Not an error condition
- Meta still includes total count (0)

---

## Query Optimization

### Required Indexes
```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

### Performance Notes
- Query is always scoped by user_id (indexed)
- Pagination prevents large result sets
- Count query runs separately for accurate totals

---

## Testing

### Unit Tests

```python
def test_list_tasks_returns_user_tasks_only():
    """Only returns tasks for specified user."""
    # Create tasks for user A and user B
    result = skill.execute(ListTasksInput(user_id=user_a_id))

    for task in result.tasks:
        assert task.user_id == user_a_id

def test_list_tasks_empty_returns_empty_array():
    """Returns empty array when no tasks exist."""
    result = skill.execute(ListTasksInput(user_id=new_user_id))

    assert result.success is True
    assert result.tasks == []
    assert result.meta.total == 0

def test_list_tasks_filter_by_completed():
    """Filters tasks by completion status."""
    result = skill.execute(ListTasksInput(
        user_id=user_id,
        filters={"completed": True}
    ))

    for task in result.tasks:
        assert task.completed is True

def test_list_tasks_default_sort_newest_first():
    """Tasks sorted by created_at desc by default."""
    result = skill.execute(ListTasksInput(user_id=user_id))

    dates = [task.created_at for task in result.tasks]
    assert dates == sorted(dates, reverse=True)

def test_list_tasks_pagination():
    """Pagination returns correct subset."""
    result = skill.execute(ListTasksInput(
        user_id=user_id,
        pagination={"limit": 10, "offset": 5}
    ))

    assert len(result.tasks) <= 10
    assert result.meta.offset == 5
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
