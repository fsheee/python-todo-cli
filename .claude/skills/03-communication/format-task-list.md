# Skill Specification: Format Task List

> **Skill ID:** SKILL-FORMAT-TASK-LIST-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Communication skill for formatting task lists for conversational display. This skill takes task data and formats it as readable text for the AI chatbot response. Supports multiple styles (concise, numbered, detailed).

---

## Skill Configuration

```yaml
skill:
  id: format-task-list
  name: Format Task List
  version: 1.0.0
  description: Format task list for conversational display with emoji and styling

  # Skill type
  type: atomic
  category: communication

  # Dependencies
  requires: []
```

---

## Input Schema

```typescript
interface FormatTaskListInput {
  tasks: Array<{
    id: string;
    title: string;
    description?: string;
    status: "pending" | "completed";
    priority: "low" | "medium" | "high";
    due_date?: string;
  }>;
  style: "concise" | "numbered" | "detailed";  // Default: "concise"
  include_emoji: boolean;                      // Default: true
}
```

---

## Output Schema

```typescript
interface FormatTaskListOutput {
  success: boolean;
  formatted_list: string;      // Formatted task list text
  task_count: number;
  completed_count: number;
  pending_count: number;
  error?: {
    code: string;
    message: string;
  };
}
```

---

## Implementation

### Python

```python
from pydantic import BaseModel
from typing import Optional

class TaskItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[str] = None

class FormatTaskListInput(BaseModel):
    tasks: list
    style: str = "concise"
    include_emoji: bool = True

class FormatTaskListOutput(BaseModel):
    success: bool
    formatted_list: str
    task_count: int
    completed_count: int
    pending_count: int
    error: dict | None = None

class FormatTaskListSkill:
    """Skill for formatting task lists for display."""

    def __init__(self):
        pass

    async def execute(
        self,
        input: FormatTaskListInput
    ) -> FormatTaskListOutput:
        """Execute the format task list skill."""

        if not input.tasks:
            return FormatTaskListOutput(
                success=True,
                formatted_list="You have no tasks yet.",
                task_count=0,
                completed_count=0,
                pending_count=0
            )

        # Parse task items
        task_items = [TaskItem(**task) for task in input.tasks]

        # Count statuses
        completed_count = sum(1 for t in task_items if t.status == "completed")
        pending_count = sum(1 for t in task_items if t.status == "pending")

        # Format based on style
        if input.style == "numbered":
            formatted = self._format_numbered(task_items, input.include_emoji)
        elif input.style == "detailed":
            formatted = self._format_detailed(task_items, input.include_emoji)
        else:
            formatted = self._format_concise(task_items, input.include_emoji)

        return FormatTaskListOutput(
            success=True,
            formatted_list=formatted,
            task_count=len(task_items),
            completed_count=completed_count,
            pending_count=pending_count
        )

    def _format_concise(self, tasks: list, include_emoji: bool) -> str:
        """Format tasks in concise style."""
        lines = []

        for task in tasks:
            status_emoji = "✅" if task.status == "completed" and include_emoji else ("○" if include_emoji else "[ ]")
            priority = ""
            if include_emoji:
                if task.priority == "high":
                    priority = " 🔴"
                elif task.priority == "low":
                    priority = " 🟢"

            lines.append(f"{status_emoji} {task.title}{priority}")

        return "\n".join(lines)

    def _format_numbered(self, tasks: list, include_emoji: bool) -> str:
        """Format tasks in numbered style."""
        lines = [""]
        for i, task in enumerate(tasks):
            status_emoji = "✅" if task.status == "completed" and include_emoji else ("○" if include_emoji else "[ ]")
            priority = ""
            if include_emoji:
                if task.priority == "high":
                    priority = " 🔴 High"
                elif task.priority == "low":
                    priority = " 🟢 Low"
            due = f" 📅 {task.due_date}" if task.due_date and include_emoji else ""
            lines.append(f"{i + 1}. {status_emoji} {task.title}{priority}{due}")

        return "\n".join(lines)

    def _format_detailed(self, tasks: list, include_emoji: bool) -> str:
        """Format tasks in detailed style."""
        lines = []

        for task in tasks:
            status = "✅ Completed" if task.status == "completed" and include_emoji else ("○ Pending" if include_emoji else "Pending")
            if not include_emoji:
                status = "Completed" if task.status == "completed" else "Pending"

            if include_emoji:
                if task.priority == "high":
                    priority = "🔴 High Priority"
                elif task.priority == "low":
                    priority = "🟢 Low Priority"
                else:
                    priority = "🟡 Medium Priority"
            else:
                priority = f"{task.priority.capitalize()} Priority"

            due = f"📅 Due: {task.due_date}" if task.due_date else ""

            lines.append(f"━━━ {task.title} ━━━")
            lines.append(f"Status: {status}")
            lines.append(f"Priority: {priority}")
            if due:
                lines.append(due)
            if task.description:
                desc = task.description if not include_emoji else f"📝 {task.description}"
                lines.append(f"Description: {desc}")
            lines.append("")

        return "\n".join(lines).strip()
```

---

## Behavior

### Success Flow

```
1. Receive list of tasks with optional style preference
2. Count completed vs pending
3. Format based on style (concise/numbered/detailed)
4. Return formatted text with counts
```

### Error Flow

```
1. Invalid style → Use default "concise"
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| No database | Read-only formatting |
| No state change | Stateless operation |

---

## Idempotency

**This skill is idempotent.** Same tasks always produce same formatted output.

---

## Reuse Across Phases

### Phase 3 (Chatbot)

- Used to format task lists in AI responses
- Supports multiple display styles

### Not Used in Phase 2

- Phase 2 uses React components for display

---

## Testing

### Unit Tests

```python
def test_format_task_list_empty():
    """Handles empty task list."""
    input = FormatTaskListInput(tasks=[], style="concise")
    result = skill.execute(input)

    assert result.success is True
    assert result.task_count == 0
    assert "no tasks" in result.formatted_list.lower()

def test_format_task_list_concise():
    """Formats tasks in concise style."""
    input = FormatTaskListInput(
        tasks=[
            {"id": "1", "title": "Task 1", "status": "pending", "priority": "high"},
            {"id": "2", "title": "Task 2", "status": "completed", "priority": "low"},
        ],
        style="concise"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task_count == 2
    assert result.pending_count == 1
    assert result.completed_count == 1

def test_format_task_list_numbered():
    """Formats tasks in numbered style."""
    input = FormatTaskListInput(
        tasks=[{"id": "1", "title": "Task 1", "status": "pending", "priority": "high"}],
        style="numbered"
    )
    result = skill.execute(input)

    assert result.success is True
    assert "1." in result.formatted_list

def test_format_task_list_with_counts():
    """Returns correct counts."""
    input = FormatTaskListInput(
        tasks=[
            {"id": "1", "title": "Task 1", "status": "pending", "priority": "medium"},
            {"id": "2", "title": "Task 2", "status": "pending", "priority": "medium"},
            {"id": "3", "title": "Task 3", "status": "completed", "priority": "medium"},
        ],
        style="concise"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.task_count == 3
    assert result.pending_count == 2
    assert result.completed_count == 1
```

---

## Related Specifications

- `/specs/features/chatbot.md` - Chatbot feature specification
- `/specs/agents/todo-agent.md` - Parent agent

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-31 | Claude | Initial specification |
