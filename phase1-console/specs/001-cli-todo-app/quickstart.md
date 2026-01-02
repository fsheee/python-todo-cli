# Quickstart: CLI Todo Application - Phase I

**Feature**: 001-cli-todo-app
**Date**: 2025-12-06

## Prerequisites

- Python 3.13+
- uv (package manager)

## Setup

```bash
# Clone the repository
git clone https://github.com/fsheee/python-todo-cli.git
cd python-todo-cli

# Install dependencies (dev only - no production deps)
uv sync
```

## Running the Application

```bash
# Run the todo app
uv run python src/main.py
```

## Usage Example

```text
╔════════════════════════════════════════╗
║         TODO APP - Phase I             ║
╠════════════════════════════════════════╣
║  1. View all tasks                     ║
║  2. Add new task                       ║
║  3. Update task                        ║
║  4. Delete task                        ║
║  5. Toggle complete/incomplete         ║
║  6. Exit                               ║
╚════════════════════════════════════════╝
Enter choice (1-6): 2

Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
✓ Task added successfully (ID: 1)

Enter choice (1-6): 1

ID  Status  Title                Description
─────────────────────────────────────────────────────
1   [ ]     Buy groceries        Milk, eggs, bread
─────────────────────────────────────────────────────
Total: 1 tasks (0 complete, 1 incomplete)

Enter choice (1-6): 5

Enter task ID to toggle: 1
✓ Task 1 marked as complete

Enter choice (1-6): 1

ID  Status  Title                Description
─────────────────────────────────────────────────────
1   [X]     Buy groceries        Milk, eggs, bread
─────────────────────────────────────────────────────
Total: 1 tasks (1 complete, 0 incomplete)

Enter choice (1-6): 6
Goodbye!
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/unit/test_task_service.py
```

## Project Structure

```text
python-todo-cli/
├── src/
│   ├── main.py              # Entry point
│   ├── models/
│   │   └── task.py          # Task dataclass
│   ├── services/
│   │   └── task_service.py  # Business logic
│   └── cli/
│       └── commands.py      # CLI handlers
├── tests/
│   ├── unit/
│   └── integration/
├── specs/
│   └── 001-cli-todo-app/    # Feature documentation
└── pyproject.toml
```

## Limitations (Phase I)

- **No persistence**: All tasks are lost when the application exits
- **Single user**: No authentication or multi-user support
- **In-memory only**: No database or file storage
- **Basic CLI**: Text-based menu, no rich terminal UI

## Troubleshooting

### "Command not found: uv"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Python version not found"

Ensure Python 3.13+ is installed:
```bash
python --version
```

### Tests fail with import errors

Ensure you're running from the project root:
```bash
cd python-todo-cli
uv run pytest
```
