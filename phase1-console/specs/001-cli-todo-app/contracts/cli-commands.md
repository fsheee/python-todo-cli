# CLI Commands Contract: CLI Todo Application - Phase I

**Feature**: 001-cli-todo-app
**Date**: 2025-12-06
**Interface**: Interactive menu-driven CLI

## Menu Structure

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
Enter choice (1-6):
```

## Command Contracts

### CMD-001: View All Tasks

**Menu Option**: 1
**Trigger**: User enters "1" at main menu

**Input**: None

**Output (empty list)**:
```text
No tasks found.
```

**Output (with tasks)**:
```text
ID  Status  Title                Description
─────────────────────────────────────────────────────
1   [ ]     Buy groceries        Milk, eggs, bread
2   [X]     Review PR
3   [ ]     Call mom             Birthday next week
─────────────────────────────────────────────────────
Total: 3 tasks (1 complete, 2 incomplete)
```

**Status Indicators**:
- `[ ]` = Incomplete
- `[X]` = Complete

---

### CMD-002: Add New Task

**Menu Option**: 2
**Trigger**: User enters "2" at main menu

**Input Flow**:
```text
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
```

**Output (success)**:
```text
✓ Task added successfully (ID: 1)
```

**Output (validation error)**:
```text
✗ Error: Title cannot be empty
```

**Validation**:
- Title is required (non-empty)
- Description is optional (empty string allowed)

---

### CMD-003: Update Task

**Menu Option**: 3
**Trigger**: User enters "3" at main menu

**Input Flow**:
```text
Enter task ID to update: 1
Enter new title (or press Enter to keep current): Buy organic groceries
Enter new description (or press Enter to keep current):
```

**Output (success)**:
```text
✓ Task 1 updated successfully
```

**Output (not found)**:
```text
✗ Error: Task not found (ID: 99)
```

**Output (invalid ID)**:
```text
✗ Error: Invalid task ID
```

**Behavior**:
- Empty input keeps existing value
- At least one field must change (title or description)

---

### CMD-004: Delete Task

**Menu Option**: 4
**Trigger**: User enters "4" at main menu

**Input Flow**:
```text
Enter task ID to delete: 1
```

**Output (success)**:
```text
✓ Task 1 deleted successfully
```

**Output (not found)**:
```text
✗ Error: Task not found (ID: 99)
```

**Output (invalid ID)**:
```text
✗ Error: Invalid task ID
```

---

### CMD-005: Toggle Complete/Incomplete

**Menu Option**: 5
**Trigger**: User enters "5" at main menu

**Input Flow**:
```text
Enter task ID to toggle: 1
```

**Output (marked complete)**:
```text
✓ Task 1 marked as complete
```

**Output (marked incomplete)**:
```text
✓ Task 1 marked as incomplete
```

**Output (not found)**:
```text
✗ Error: Task not found (ID: 99)
```

**Output (invalid ID)**:
```text
✗ Error: Invalid task ID
```

---

### CMD-006: Exit

**Menu Option**: 6
**Trigger**: User enters "6" at main menu

**Output**:
```text
Goodbye!
```

**Behavior**: Application terminates, all data is lost.

---

## Error Messages

| Code | Message | Trigger |
|------|---------|---------|
| E001 | "Title cannot be empty" | Empty title on add/update |
| E002 | "Task not found (ID: {id})" | Invalid ID on get/update/delete/toggle |
| E003 | "Invalid task ID" | Non-numeric input for ID |
| E004 | "Invalid choice. Please enter 1-6." | Invalid menu selection |

## Input Validation

| Field | Validation | Error |
|-------|------------|-------|
| Menu choice | Must be 1-6 | E004 |
| Task ID | Must be positive integer | E003 |
| Title | Must be non-empty | E001 |
| Description | Any string (optional) | None |
