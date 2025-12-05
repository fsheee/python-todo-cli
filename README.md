# Todo CLI Application - Phase I

A command-line todo application with in-memory storage.

## Features

- View all tasks with status indicators
- Add new tasks with title and description
- Update task details
- Delete tasks
- Toggle complete/incomplete status

## Requirements

- Python 3.13+
- uv (package manager)

## Running the Application

```bash
uv run python src/main.py
```

## Usage

```
1. View all tasks
2. Add new task
3. Update task
4. Delete task
5. Toggle complete/incomplete
6. Exit
```

## Testing

Run all tests:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

### Test Coverage

| File | Tests | Coverage |
|------|-------|----------|
| `tests/test_task.py` | 4 | Task dataclass |
| `tests/test_task_service.py` | 22 | CRUD operations |
| `tests/test_commands.py` | 8 | ID parsing/validation |
| **Total** | **34** | All passing |

## Limitations (Phase I)

- No persistence - all tasks are lost when the application exits
- Single user - no authentication
- In-memory storage only
