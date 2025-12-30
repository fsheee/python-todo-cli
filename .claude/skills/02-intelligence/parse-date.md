# Skill Specification: Parse Date

> **Skill ID:** SKILL-PARSE-DATE-001
> **Version:** 1.0.0
> **Status:** Draft
> **Last Updated:** 2025-12-31

---

## Overview

Intelligence skill for parsing natural language date references into ISO 8601 format. This skill understands expressions like "tomorrow", "next Friday", "in 3 days", etc. Used by Phase 3 chatbot to extract due dates from natural language.

---

## Skill Configuration

```yaml
skill:
  id: parse-date
  name: Parse Date
  version: 1.0.0
  description: Parse natural language date references into ISO 8601 format

  # Skill type
  type: atomic
  category: intelligence

  # Dependencies
  requires: []
```

---

## Input Schema

```typescript
interface ParseDateInput {
  text: string;             // Date text to parse (e.g., "tomorrow", "next Friday")
}
```

### Supported Formats

| Format | Example | Output |
|--------|---------|--------|
| Relative | "tomorrow" | 2025-01-01T00:00:00 |
| Relative | "next Friday" | 2025-01-03T00:00:00 |
| Relative | "in 3 days" | 2025-01-03T00:00:00 |
| Relative | "tonight" | 2025-12-31T20:00:00 |
| Relative | "end of week" | 2025-01-05T23:59:59 |
| ISO | "2025-01-15" | 2025-01-15T00:00:00 |

---

## Output Schema

```typescript
interface ParseDateOutput {
  success: boolean;
  iso_date?: string;        // ISO 8601 date or null
  is_relative: boolean;     // True if relative date (tomorrow, etc.)
  original_text: string;    // Original input text
  parsed_description: string;  // Human-readable description
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
from datetime import datetime, timedelta
from pydantic import BaseModel
import re

class ParseDateInput(BaseModel):
    text: str

class ParseDateOutput(BaseModel):
    success: bool
    iso_date: str | None = None
    is_relative: bool = False
    original_text: str = ""
    parsed_description: str = ""
    error: dict | None = None

class ParseDateSkill:
    """Skill for parsing natural language dates."""

    def __init__(self):
        self.days_of_week = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
        }

    async def execute(self, input: ParseDateInput) -> ParseDateOutput:
        """Execute the parse date skill."""

        text = input.text.lower().strip()
        original_text = text

        if not text:
            return ParseDateOutput(
                success=True,
                iso_date=None,
                is_relative=False,
                original_text="",
                parsed_description="No date specified"
            )

        # Parse the date
        result = self._parse_date(text)

        return ParseDateOutput(
            success=True,
            iso_date=result.get("iso_date"),
            is_relative=result.get("is_relative", False),
            original_text=original_text,
            parsed_description=result.get("description", text)
        )

    def _parse_date(self, text: str) -> dict:
        """Parse date text and return result."""
        now = datetime.now()

        # Exact time references
        time_refs = {
            "now": ("today", lambda: now),
            "today": ("today", lambda: now),
            "tonight": ("tonight", lambda: now.replace(hour=20, minute=0)),
            "tomorrow": ("tomorrow", lambda: now + timedelta(days=1)),
            "tomorrow morning": ("tomorrow morning", lambda: (now + timedelta(days=1)).replace(hour=9, minute=0)),
            "this afternoon": ("this afternoon", lambda: now.replace(hour=14, minute=0)),
            "this evening": ("this evening", lambda: now.replace(hour=18, minute=0)),
            "end of day": ("end of day", lambda: now.replace(hour=23, minute=59)),
            "end of week": ("end of week", lambda: now + timedelta(days=(4 - now.weekday()) % 7 or 7)),
        }

        for pattern, (desc, handler) in time_refs.items():
            if pattern in text:
                dt = handler()
                return {
                    "iso_date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_relative": True,
                    "description": desc
                }

        # "in X days/weeks"
        in_pattern = r"in\s+(\d+)\s+(day|week|month|hour)s?"
        match = re.search(in_pattern, text)
        if match:
            amount = int(match.group(1))
            unit = match.group(2)
            if unit == "day":
                dt = now + timedelta(days=amount)
            elif unit == "week":
                dt = now + timedelta(weeks=amount)
            elif unit == "hour":
                dt = now + timedelta(hours=amount)
            else:
                dt = now

            return {
                "iso_date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "is_relative": True,
                "description": f"in {amount} {unit}s"
            }

        # Day of week
        for day_name, day_num in self.days_of_week.items():
            if re.search(rf"\b{day_name}\b", text):
                current_weekday = now.weekday()
                days_ahead = day_num - current_weekday
                if days_ahead <= 0:
                    days_ahead += 7

                if re.search(rf"\bnext\s+{day_name}\b", text):
                    days_ahead += 7

                dt = now + timedelta(days=days_ahead)
                is_next = re.search(rf"\bnext\s+{day_name}\b", text)

                return {
                    "iso_date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "is_relative": True,
                    "description": f"next {day_name}" if is_next else f"this {day_name}"
                }

        # Try ISO format
        try:
            dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            return {
                "iso_date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "is_relative": False,
                "description": text
            }
        except ValueError:
            pass

        # Could not parse
        return {
            "iso_date": None,
            "is_relative": False,
            "description": "Could not parse date"
        }
```

---

## Behavior

### Success Flow

```
1. Receive date text
2. Normalize text (lowercase, trim)
3. Match against known patterns
4. Calculate target date
5. Return ISO format with description
```

### Error Flow

```
1. Empty text → Return null ISO date with description
2. Unknown format → Return null ISO date
```

---

## Side Effects

| Effect | Description |
|--------|-------------|
| No database | Read-only parsing |
| No state change | Stateless operation |

---

## Idempotency

**This skill is idempotent.** Same input always returns same result (time-dependent results may vary).

---

## Reuse Across Phases

### Phase 3 (Chatbot)

- Used when parsing due dates from user messages
- Called by extract-entities skill
- Returns standardized ISO dates for storage

### Not Used in Phase 2

- Phase 2 receives dates in ISO format from API

### Reused Components

- Date parsing logic (shared)
- ISO format standardization (consistent)

---

## Testing

### Unit Tests

```python
def test_parse_date_tomorrow():
    """Parses 'tomorrow' correctly."""
    input = ParseDateInput(text="tomorrow")
    result = skill.execute(input)

    assert result.success is True
    assert result.is_relative is True
    assert "tomorrow" in result.parsed_description
    assert result.iso_date is not None

def test_parse_date_next_friday():
    """Parses 'next Friday' correctly."""
    input = ParseDateInput(text="next Friday")
    result = skill.execute(input)

    assert result.success is True
    assert result.is_relative is True
    assert "friday" in result.parsed_description.lower()

def test_parse_date_in_3_days():
    """Parses 'in 3 days' correctly."""
    input = ParseDateInput(text="in 3 days")
    result = skill.execute(input)

    assert result.success is True
    assert result.is_relative is True
    assert "3 days" in result.parsed_description

def test_parse_date_iso():
    """Parses ISO date format."""
    input = ParseDateInput(text="2025-01-15")
    result = skill.execute(input)

    assert result.success is True
    assert result.is_relative is False
    assert "2025-01-15" in result.iso_date

def test_parse_date_empty():
    """Handles empty input."""
    input = ParseDateInput(text="")
    result = skill.execute(input)

    assert result.success is True
    assert result.iso_date is None
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
