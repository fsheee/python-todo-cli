# Data Model: CLI Todo Application - Phase I

**Feature**: 001-cli-todo-app
**Date**: 2025-12-06
**Storage**: In-memory (Python dict)

## Entities

### Task

The primary entity representing a todo item.

```python
@dataclass
class Task:
    id: int              # Unique identifier (auto-generated, positive integer)
    title: str           # Required, non-empty
    description: str     # Optional, can be empty string
    is_complete: bool    # Default: False
```

#### Field Specifications

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | int | Yes | Auto-generated | Positive integer, unique, immutable |
| title | str | Yes | None | Non-empty, whitespace-trimmed |
| description | str | No | "" | Any string allowed |
| is_complete | bool | No | False | Boolean toggle |

#### Validation Rules

- **VR-001**: `title` MUST NOT be empty or whitespace-only
- **VR-002**: `id` MUST be a positive integer
- **VR-003**: `id` MUST be unique within the task store

### TaskStore

In-memory storage container for tasks.

```python
class TaskStore:
    _tasks: dict[int, Task]  # ID -> Task mapping
    _next_id: int            # Counter for ID generation
```

#### State Transitions

```text
Task Lifecycle:
┌─────────────┐
│   Created   │ ─── add_task() ───▶ Stored (is_complete=False)
└─────────────┘
       │
       ▼
┌─────────────┐
│   Active    │ ◀── toggle_complete() ──▶ Complete
└─────────────┘                           │
       │                                   │
       ▼                                   ▼
┌─────────────┐                    ┌─────────────┐
│   Updated   │ ◀── update_task()  │   Updated   │
└─────────────┘                    └─────────────┘
       │                                   │
       ▼                                   ▼
┌─────────────┐                    ┌─────────────┐
│   Deleted   │ ◀── delete_task() ─│   Deleted   │
└─────────────┘                    └─────────────┘
```

## Relationships

```text
TaskStore (1) ────contains────▶ (0..*) Task
```

- One TaskStore contains zero or more Tasks
- Tasks are uniquely identified by their `id` within the store
- No relationships between Tasks (flat structure)

## Data Operations

### CRUD Operations

| Operation | Input | Output | Side Effects |
|-----------|-------|--------|--------------|
| add | title, description? | Task | Increments _next_id |
| get | id | Task or None | None |
| get_all | - | list[Task] | None |
| update | id, title?, description? | Task or None | None |
| delete | id | bool | Removes from _tasks |
| toggle_complete | id | Task or None | Flips is_complete |

### Error Conditions

| Error | Trigger | Response |
|-------|---------|----------|
| TaskNotFoundError | Invalid/missing ID | "Task not found" |
| ValidationError | Empty title | "Title cannot be empty" |
| InvalidIdError | Non-numeric ID input | "Invalid task ID" |

## Sample Data

```python
# Example task store state after several operations
{
    1: Task(id=1, title="Buy groceries", description="Milk, eggs, bread", is_complete=False),
    2: Task(id=2, title="Review PR", description="", is_complete=True),
    3: Task(id=3, title="Call mom", description="Birthday next week", is_complete=False),
}
```

## Future Considerations (Phase II)

- Persistence: Serialize dict to JSON file
- Created/updated timestamps
- Priority field
- Tags/categories
- Due dates
