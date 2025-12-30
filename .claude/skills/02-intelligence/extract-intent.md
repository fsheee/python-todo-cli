# Skill Specification: Extract Intent

> **Skill ID:** SKILL-EXTRACT-INTENT-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Intelligence skill for extracting user intent from natural language messages. This skill analyzes conversational input and identifies what action the user wants to perform. Used by Phase 3 AI chatbot to route to appropriate skills.

---

## Skill Configuration

```yaml
skill:
  id: extract-intent
  name: Extract Intent
  version: 1.0.0
  description: Extract user intent from natural language message

  # Skill type
  type: atomic
  category: intelligence

  # Dependencies
  requires:
    - message_context
```

---

## Input Schema

```typescript
interface ExtractIntentInput {
  message: string;           // User's message to analyze
  context_messages?: Array<{
    role: "user" | "assistant";
    content: string;
  }>;                        // Conversation history for context
}
```

### Validation Rules

| Field | Rule | Error Message | Default |
|-------|------|---------------|---------|
| `message` | Required | "Message is required" | - |

---

## Output Schema

```typescript
interface ExtractIntentOutput {
  success: boolean;
  intent: "CREATE_TODO" | "LIST_TODOS" | "UPDATE_TODO" |
          "DELETE_TODO" | "COMPLETE_TODO" | "SEARCH_TODOS" |
          "GET_DETAILS" | "HELP" | "GREETING" | "UNKNOWN";
  confidence: number;        // 0.0 to 1.0
  entities?: {
    action?: string;         // Extracted action type
    has_context?: boolean;   // Has conversation context
    reference_type?: string; // "first", "second", "last", "reference"
  };
  suggested_response?: string;
  error?: {
    code: string;
    message: string;
  };
}
```

### Intent Types

| Intent | Description | Example |
|--------|-------------|---------|
| `CREATE_TODO` | User wants to create a task | "Add buy groceries" |
| `LIST_TODOS` | User wants to see tasks | "Show my tasks" |
| `UPDATE_TODO` | User wants to modify a task | "Change priority to high" |
| `DELETE_TODO` | User wants to remove a task | "Delete the first one" |
| `COMPLETE_TODO` | User wants to mark complete | "Mark as done" |
| `SEARCH_TODOS` | User wants to search tasks | "Find tasks about groceries" |
| `GET_DETAILS` | User wants task details | "Show details for task 1" |
| `HELP` | User wants help | "What can you do?" |
| `GREETING` | User is greeting | "Hi, hello" |
| `UNKNOWN` | Could not determine intent | - |

---

## Implementation

### Python (Pattern Matching)

```python
from pydantic import BaseModel
from typing import Optional
import re

class ExtractIntentInput(BaseModel):
    message: str
    context_messages: list | None = None

class ExtractIntentOutput(BaseModel):
    success: bool
    intent: str
    confidence: float
    entities: dict | None = None
    suggested_response: str | None = None
    error: dict | None = None

class ExtractIntentSkill:
    """Skill for extracting user intent from natural language."""

    def __init__(self):
        # Intent patterns
        self.patterns = {
            "CREATE_TODO": [
                r"add\s+(?:a\s+)?task",
                r"create\s+(?:a\s+)?task",
                r"new\s+task",
                r"i need to",
                r"remind me to",
            ],
            "LIST_TODOS": [
                r"show\s+(?:my\s+)?tasks",
                r"list\s+(?:my\s+)?tasks",
                r"what('s|\s+is)\s+(?:my\s+)?tasks",
                r"get\s+(?:my\s+)?tasks",
                r"view\s+(?:my\s+)?tasks",
            ],
            "DELETE_TODO": [
                r"delete",
                r"remove",
                r"get rid of",
            ],
            "COMPLETE_TODO": [
                r"complete",
                r"finish",
                r"done",
                r"mark\s+(?:as\s+)?done",
            ],
            "UPDATE_TODO": [
                r"change\s+(?:the\s+)?",
                r"update\s+(?:the\s+)?",
                r"modify\s+(?:the\s+)?",
            ],
            "SEARCH_TODOS": [
                r"search\s+(?:for\s+)?",
                r"find\s+(?:my\s+)?",
                r"look\s+for",
            ],
            "HELP": [
                r"help",
                r"what can you do",
                r"how do i",
            ],
            "GREETING": [
                r"^(hi|hello|hey|good morning|good afternoon)",
            ],
        }

    async def execute(self, input: ExtractIntentInput) -> ExtractIntentOutput:
        """Execute the extract intent skill."""

        if not input.message:
            return ExtractIntentOutput(
                success=False,
                intent="UNKNOWN",
                confidence=0.0,
                error={
                    "code": "VALIDATION_ERROR",
                    "message": "Message is required"
                }
            )

        message = input.message.lower().strip()
        entities = {"original_message": message}

        # Check each intent pattern
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    confidence = self._calculate_confidence(intent, message)

                    # Check for context references
                    if intent == "UNKNOWN" and input.context_messages:
                        intent, confidence = self._check_context_references(
                            message,
                            input.context_messages,
                            entities
                        )

                    return ExtractIntentOutput(
                        success=True,
                        intent=intent,
                        confidence=confidence,
                        entities=entities,
                        suggested_response=self._suggest_response(intent)
                    )

        # Default to unknown
        return ExtractIntentOutput(
            success=True,
            intent="UNKNOWN",
            confidence=0.3,
            entities=entities
        )

    def _calculate_confidence(self, intent: str, message: str) -> float:
        """Calculate confidence score based on pattern match."""
        base_confidence = {
            "CREATE_TODO": 0.85,
            "LIST_TODOS": 0.85,
            "DELETE_TODO": 0.8,
            "COMPLETE_TODO": 0.8,
            "UPDATE_TODO": 0.75,
            "SEARCH_TODOS": 0.8,
            "HELP": 0.9,
            "GREETING": 0.95,
        }
        return base_confidence.get(intent, 0.5)

    def _check_context_references(
        self,
        message: str,
        context_messages: list,
        entities: dict
    ) -> tuple[str, float]:
        """Check for context references like 'the first one', 'it', etc."""
        reference_patterns = [
            (r"^(the\s+)?first(?:\s+one)?$", "first"),
            (r"^(the\s+)?second(?:\s+one)?$", "second"),
            (r"^(the\s+)?third(?:\s+one)?$", "third"),
            (r"^(the\s+)?last(?:\s+one)?$", "last"),
            (r"^(it|that|them)$", "reference"),
        ]

        for pattern, ref_type in reference_patterns:
            if re.search(pattern, message):
                entities["has_context"] = True
                entities["reference_type"] = ref_type

                # Infer intent from context
                if len(context_messages) >= 2:
                    last_user_msg = context_messages[-1].get("content", "").lower()
                    if "complete" in last_user_msg or "done" in last_user_msg:
                        return "COMPLETE_TODO", 0.7
                    if "delete" in last_user_msg or "remove" in last_user_msg:
                        return "DELETE_TODO", 0.7

                return "UNKNOWN", 0.5

        return "UNKNOWN", 0.3

    def _suggest_response(self, intent: str) -> str:
        """Suggest initial response based on intent."""
        suggestions = {
            "CREATE_TODO": "I'll help you create a task. What should it be called?",
            "LIST_TODOS": "Here are your tasks.",
            "DELETE_TODO": "Which task would you like to delete?",
            "COMPLETE_TODO": "Which task would you like to complete?",
            "UPDATE_TODO": "What would you like to change?",
            "SEARCH_TODOS": "What are you looking for?",
            "HELP": "I can help you manage your tasks.",
            "GREETING": "Hello! How can I help you with your tasks today?",
            "UNKNOWN": "I'm not sure what you mean. Can you rephrase?",
        }
        return suggestions.get(intent)
```

---

## Behavior

### Success Flow

```
1. Receive user's message and optional context
2. Normalize message (lowercase, trim)
3. Match against intent patterns
4. Calculate confidence score
5. Check for context references
6. Return intent with confidence and entities
```

### Error Flow

```
1. Empty message → Return UNKNOWN with error
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| No database | Read-only analysis |
| No state change | Stateless operation |

---

## Idempotency

**This skill is idempotent.** Same message always returns same intent.

---

## Reuse Across Phases

### Phase 3 (Chatbot)

- Used by AI agent to route user requests
- Called before selecting MCP tool
- Supports conversation context

### Not Used in Phase 2

- Phase 2 uses direct REST API calls
- No natural language processing needed

### Reused Components

- Pattern matching logic (can be enhanced with ML)
- Intent taxonomy (consistent across phases)

---

## Testing

### Unit Tests

```python
def test_extract_intent_create():
    """Extracts CREATE_TODO intent from creation request."""
    input = ExtractIntentInput(message="Add buy groceries")
    result = skill.execute(input)

    assert result.success is True
    assert result.intent == "CREATE_TODO"
    assert result.confidence >= 0.8

def test_extract_intent_list():
    """Extracts LIST_TODOS intent from list request."""
    input = ExtractIntentInput(message="Show my tasks")
    result = skill.execute(input)

    assert result.success is True
    assert result.intent == "LIST_TODOS"

def test_extract_intent_greeting():
    """Extracts GREETING intent."""
    input = ExtractIntentInput(message="Hi there!")
    result = skill.execute(input)

    assert result.success is True
    assert result.intent == "GREETING"
    assert result.confidence >= 0.9

def test_extract_intent_with_context():
    """Handles context references like 'the first one'."""
    input = ExtractIntentInput(
        message="the first one",
        context_messages=[
            {"role": "assistant", "content": "Here are your tasks..."},
            {"role": "user", "content": "Show my tasks"},
        ]
    )
    result = skill.execute(input)

    assert result.success is True
    assert result.entities.has_context is True
    assert result.entities.reference_type == "first"

def test_extract_intent_empty():
    """Returns error for empty message."""
    input = ExtractIntentInput(message="")
    result = skill.execute(input)

    assert result.success is False
    assert result.error.code == "VALIDATION_ERROR"
```

---

## Related Specifications

- `/specs/features/chatbot.md` - Chatbot feature specification
- `/specs/agents/todo-agent.md` - Parent agent
- `/specs/api/mcp-tools.md` - MCP tool wrapper

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-31 | Claude | Initial specification |
