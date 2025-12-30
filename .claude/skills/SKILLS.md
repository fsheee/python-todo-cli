# Skills Index

> **Master Skills Document**
> **Version:** 1.0.0
> **Last Updated:** 2025-12-31

---

## Overview

This document provides an index of all reusable skills for the hackathon-todo project. Skills are organized by category and designed for reuse across Phase 2 (web backend) and Phase 3 (chatbot).

## Directory Structure

```
.claude/skills/
├── SKILLS.md                    # This master index
├── 01-core/
│   ├── task/
│   │   ├── create-task.md       # Create a new task
│   │   ├── list-tasks.md        # List tasks with filters
│   │   ├── update-task.md       # Update task fields
│   │   ├── delete-task.md       # Delete a task
│   │   └── toggle-complete.md   # Toggle completion status
│   └── user/
│       └── verify-jwt.md        # Verify JWT tokens
├── 02-intelligence/
│   ├── extract-intent.md        # Extract user intent from NL
│   └── parse-date.md            # Parse natural language dates
└── 03-communication/
    ├── format-task-list.md      # Format tasks for display
    └── generate-response.md     # Generate NL responses
```

---

## Skills by Category

### Core Task Skills

| Skill ID | Name | Type | Destructive | Phase | File |
|----------|------|------|-------------|-------|------|
| `create-task` | Create Task | atomic | No | 2/3 | [01-core/task/create-task.md](./01-core/task/create-task.md) |
| `list-tasks` | List Tasks | atomic | No | 2/3 | [01-core/task/list-tasks.md](./01-core/task/list-tasks.md) |
| `update-task` | Update Task | atomic | No | 2/3 | [01-core/task/update-task.md](./01-core/task/update-task.md) |
| `delete-task` | Delete Task | atomic | Yes | 2/3 | [01-core/task/delete-task.md](./01-core/task/delete-task.md) |
| `toggle-complete` | Toggle Complete | atomic | No | 2/3 | [01-core/task/toggle-complete.md](./01-core/task/toggle-complete.md) |

### Core User Skills

| Skill ID | Name | Type | Phase | File |
|----------|------|------|-------|------|
| `verify-jwt` | Verify JWT | atomic | 2/3 | [01-core/user/verify-jwt.md](./01-core/user/verify-jwt.md) |

### Intelligence Skills (Phase 3)

| Skill ID | Name | Type | Phase | File |
|----------|------|------|-------|------|
| `extract-intent` | Extract Intent | atomic | 3 | [02-intelligence/extract-intent.md](./02-intelligence/extract-intent.md) |
| `parse-date` | Parse Date | atomic | 3 | [02-intelligence/parse-date.md](./02-intelligence/parse-date.md) |

### Communication Skills (Phase 3)

| Skill ID | Name | Type | Phase | File |
|----------|------|------|-------|------|
| `format-task-list` | Format Task List | atomic | 3 | [03-communication/format-task-list.md](./03-communication/format-task-list.md) |
| `generate-response` | Generate Response | atomic | 3 | [03-communication/generate-response.md](./03-communication/generate-response.md) |

---

## Skill Specification Template

All skills follow this standardized format:

```markdown
# Skill Specification: [SKILL NAME]

> **Skill ID:** SKILL-[NAME]-[NUMBER]
> **Version:** 1.0.0
> **Status:** Draft | Review | Approved
> **Last Updated:** YYYY-MM-DD

---

## Overview

Brief description of what the skill does.

---

## Skill Configuration

```yaml
skill:
  id: skill-id
  name: Skill Name
  version: 1.0.0
  description: Brief description

  type: atomic | composite | workflow
  category: task | user | intelligence | communication

  destructive: true | false

  requires:
    - database_session
    - user_context
```

---

## Input Schema

```typescript
interface SkillNameInput {
  field1: string;  // Description
  field2?: number; // Optional field
}
```

---

## Output Schema

```typescript
interface SkillNameOutput {
  success: boolean;
  data?: {...};
  error?: {...};
}
```

---

## Implementation

Python implementation code.

---

## Behavior

### Success Flow
1. Step 1
2. Step 2

### Error Flow
1. Condition → Result

---

## Side Effects

| Effect | Description |
|--------|-------------|
| Database INSERT/UPDATE/DELETE | Description |

---

## Idempotency

This skill is [NOT] idempotent.

---

## Reuse Across Phases

### Phase 2 (Web Backend)
- Used by FastAPI endpoint `ENDPOINT`

### Phase 3 (Chatbot)
- Wrapped as MCP tool `tool_name`
- Called by AI agent for...

### Reused Components
- Validation logic
- Response format

---

## Testing

Unit and integration tests.

---

## Related Specifications

- `/specs/features/...`
- `/specs/agents/...`
- `/specs/api/...`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | YYYY-MM-DD | Name | Initial specification |
```

---

## Phase Compatibility Matrix

| Skill | Phase 2 (Web) | Phase 3 (Chatbot) | Notes |
|-------|---------------|-------------------|-------|
| `create-task` | ✅ Direct | ✅ MCP (`create_todo`) | Shared validation |
| `list-tasks` | ✅ Direct | ✅ MCP (`list_todos`) | Shared query logic |
| `update-task` | ✅ Direct | ✅ MCP (`update_todo`) | Shared validation |
| `delete-task` | ✅ Direct | ✅ MCP (`delete_todo`) | Confirmation flow |
| `toggle-complete` | ✅ Direct | ✅ MCP (`toggle_complete`) | Simplified interface |
| `verify-jwt` | ✅ FastAPI Dep | ✅ At connection | Shared JWT logic |
| `extract-intent` | ❌ | ✅ AI agent | Phase 3 only |
| `parse-date` | ❌ | ✅ extract-entities | Phase 3 only |
| `format-task-list` | ❌ | ✅ AI responses | Phase 3 only |
| `generate-response` | ❌ | ✅ AI responses | Phase 3 only |

---

## Skill Orchestration

### Sequential Chaining

```
extract-intent → parse-date → create-task → generate-response
```

### Parallel Execution

```
(get-user-context, list-tasks) → combine results
```

### Conditional Execution

```
delete-task (only if confirm=true)
```

---

## Error Codes

All skills use standardized error codes:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `INVALID_TOKEN` | 401 | Invalid JWT token |
| `TOKEN_EXPIRED` | 401 | JWT token expired |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `BACKEND_ERROR` | 500 | Backend service error |

---

## Naming Conventions

### Skill IDs
- Format: `kebab-case`
- Example: `create-task`, `list-tasks`, `extract-intent`

### File Names
- Match skill ID with `.md` extension
- Example: `create-task.md`, `extract-intent.md`

### Directory Names
- Category prefix with number for ordering
- Example: `01-core/task/`, `02-intelligence/`

---

## Adding New Skills

1. Create new `.md` file in appropriate category directory
2. Use the skill specification template above
3. Update this `SKILLS.md` index with new skill
4. Add to relevant agent specifications
5. Write unit and integration tests

---

## Related Documents

- [Project Overview](../specs/overview.md)
- [Task CRUD Feature](../specs/features/task-crud.md)
- [Chatbot Feature](../specs/features/chatbot.md)
- [REST API Endpoints](../specs/api/rest-endpoints.md)
- [MCP Tools](../specs/api/mcp-tools.md)
- [Database Schema](../specs/database/schema.md)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-31 | Claude | Initial skills index with 10 skills |
