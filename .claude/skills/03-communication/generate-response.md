# Skill Specification: Generate Response

> **Skill ID:** SKILL-GENERATE-RESPONSE-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Communication skill for generating natural language responses for the conversational interface. This skill takes skill execution results and generates appropriate human-readable responses. Supports multiple styles (friendly, formal, casual).

---

## Skill Configuration

```yaml
skill:
  id: generate-response
  name: Generate Response
  version: 1.0.0
  description: Generate natural language response for conversational interface

  # Skill type
  type: atomic
  category: communication

  # Dependencies
  requires: []
```

---

## Input Schema

```typescript
interface GenerateResponseInput {
  action: string;           // create, update, delete, list, search, error, help, greeting
  result: dict;             // Result data from skill execution
  style: "friendly" | "formal" | "casual";  // Default: "friendly"
  include_emoji: boolean;   // Default: true
}
```

---

## Output Schema

```typescript
interface GenerateResponseOutput {
  success: boolean;
  response: string;         // Generated response text
  follow_up?: string;       // Optional follow-up question
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

class GenerateResponseInput(BaseModel):
    action: str
    result: dict
    style: str = "friendly"
    include_emoji: bool = True

class GenerateResponseOutput(BaseModel):
    success: bool
    response: str
    follow_up: str | None = None
    error: dict | None = None

class GenerateResponseSkill:
    """Skill for generating natural language responses."""

    def __init__(self):
        pass

    async def execute(
        self,
        input: GenerateResponseInput
    ) -> GenerateResponseOutput:
        """Execute the generate response skill."""

        # Generate response based on action and style
        if input.style == "formal":
            response = self._generate_formal(input.action, input.result, input.include_emoji)
        elif input.style == "casual":
            response = self._generate_casual(input.action, input.result, input.include_emoji)
        else:
            response = self._generate_friendly(input.action, input.result, input.include_emoji)

        # Generate follow-up suggestion
        follow_up = self._generate_follow_up(input.action, input.result)

        return GenerateResponseOutput(
            success=True,
            response=response,
            follow_up=follow_up
        )

    def _emoji(self, emoji: str, include: bool) -> str:
        """Get emoji if enabled."""
        return emoji if include else ""

    def _generate_friendly(self, action: str, result: dict, include_emoji: bool) -> str:
        """Generate friendly response."""
        emoji = self._emoji

        if action == "create":
            title = result.get("task", {}).get("title", "this task")
            priority = result.get("task", {}).get("priority", "medium")
            priority_text = f"🔴 High priority" if priority == "high" else ("🟢 Low priority" if priority == "low" else "🟡 Medium priority")
            return f"{emoji('📝', include)} Got it! I've created \"{title}\" {priority_text}"

        elif action == "update":
            title = result.get("task", {}).get("title", "this task")
            return f"{emoji('✏️', include)} Updated! \"{title}\" has been modified."

        elif action == "complete":
            title = result.get("task", {}).get("title", "Task")
            return f"{emoji('🎉', include)} Awesome! I've marked \"{title}\" as completed. Great job! {emoji('⭐', include)}"

        elif action == "delete":
            return f"{emoji('🗑️', include)} Done! I've deleted that task."

        elif action == "list":
            tasks = result.get("tasks", [])
            count = result.get("count", len(tasks))

            if count == 0:
                return f"{emoji('✨', include)} You have no tasks! All caught up!"

            return f"{emoji('📋', include)} Here are your tasks ({count} total)"

        elif action == "search":
            query = result.get("query", "")
            count = result.get("count", 0)
            return f"{emoji('🔍', include)} Found {count} tasks matching \"{query}\""

        elif action == "error":
            code = result.get("code", "UNKNOWN")
            message = result.get("message", "Something went wrong")
            return f"{emoji('❌', include)} {message}"

        elif action == "help":
            return f"""{emoji('👋', include)} Hi! I'm your todo assistant.

{emoji('📝', include)} **Create tasks** - "Add buy groceries"
{emoji('📋', include)} **List tasks** - "Show my tasks"
{emoji('✅', include)} **Complete tasks** - "Complete the first one"
{emoji('✏️', include)} **Update tasks** - "Change priority to high"
{emoji('🗑️', include)} **Delete tasks** - "Delete the last one"
{emoji('🔍', include)} **Search tasks** - "Find tasks about groceries"

Just talk to me naturally! {emoji('😊', include)}"""

        elif action == "greeting":
            return f"{emoji('👋', include)} Hello! How can I help you with your tasks today?"

        return f"{emoji('👍', include)} Done!"

    def _generate_casual(self, action: str, result: dict, include_emoji: bool) -> str:
        """Generate casual response."""
        emoji = self._emoji

        if action == "create":
            return f"cool, added \"{result.get('task', {}).get('title', 'that')}\" to your list!"
        elif action == "update":
            return f"updated!"
        elif action == "complete":
            return f"nice one! ✅"
        elif action == "delete":
            return f"gone! 🗑️"
        elif action == "list":
            return f"here's what you've got ({result.get('count', 0)} tasks)"
        elif action == "error":
            return f"oops: {result.get('message', 'something went wrong')}"
        elif action == "help":
            return "hey! i can help you add, list, complete, search, or delete tasks. just tell me what you want!"
        return "got it!"

    def _generate_formal(self, action: str, result: dict, include_emoji: bool) -> str:
        """Generate formal response."""
        emoji = self._emoji

        if action == "create":
            return f"I have successfully created the task \"{result.get('task', {}).get('title', '')}\"."
        elif action == "update":
            return "Task has been updated successfully."
        elif action == "complete":
            return "The task has been marked as completed."
        elif action == "delete":
            return "Task has been deleted."
        elif action == "list":
            return f"Displaying {result.get('count', 0)} tasks."
        elif action == "error":
            return f"An error occurred: {result.get('message', 'Unknown error')}"
        elif action == "help":
            return "I can assist with task management operations including create, read, update, and delete."
        return "Operation completed successfully."

    def _generate_follow_up(self, action: str, result: dict) -> Optional[str]:
        """Generate follow-up suggestion."""
        suggestions = {
            "create": "Would you like to set a due date for this task?",
            "list": "Would you like me to help you complete any of these tasks?",
            "search": "Would you like me to show you all your tasks instead?",
            "error": "Would you like me to try again or do something else?",
        }
        return suggestions.get(action)
```

---

## Behavior

### Success Flow

```
1. Receive action type and result data
2. Generate response based on style preference
3. Add optional follow-up suggestion
4. Return formatted response
```

### Error Flow

```
1. Unknown action → Return generic response
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| No database | Read-only generation |
| No state change | Stateless operation |

---

## Idempotency

**This skill is idempotent.** Same action and result produce same response.

---

## Reuse Across Phases

### Phase 3 (Chatbot)

- Used to generate AI chatbot responses
- Supports multiple response styles
- Includes follow-up suggestions

### Not Used in Phase 2

- Phase 2 uses React UI components

---

## Testing

### Unit Tests

```python
def test_generate_response_create():
    """Generates response for create action."""
    input = GenerateResponseInput(
        action="create",
        result={"task": {"title": "Buy milk", "priority": "high"}},
        style="friendly"
    )
    result = skill.execute(input)

    assert result.success is True
    assert "Buy milk" in result.response
    assert "created" in result.response.lower()

def test_generate_response_list_empty():
    """Generates response for empty list."""
    input = GenerateResponseInput(
        action="list",
        result={"tasks": [], "count": 0},
        style="friendly"
    )
    result = skill.execute(input)

    assert result.success is True
    assert "no tasks" in result.response.lower()

def test_generate_response_error():
    """Generates error response."""
    input = GenerateResponseInput(
        action="error",
        result={"code": "NOT_FOUND", "message": "Task not found"},
        style="friendly"
    )
    result = skill.execute(input)

    assert result.success is True
    assert "not found" in result.response.lower()

def test_generate_response_follow_up():
    """Includes follow-up suggestion."""
    input = GenerateResponseInput(
        action="create",
        result={"task": {"title": "Test"}},
        style="friendly"
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.follow_up is not None
    assert "due date" in result.follow_up.lower()
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
