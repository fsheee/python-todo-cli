---
name: create-task
description: Create a new task. Use when user wants to add a new todo item.
---

When creating a task:

1. **Required**: user_id, title (1-255 chars)
2. **Optional**: description (0-2000 chars), priority (low/medium/high), due_date (ISO 8601)
3. **Default**: priority="medium", status="pending"

Input:
```typescript
{ user_id, title, description?, priority?, due_date? }
```

Response includes created task with id, created_at timestamp.

Validate title is not empty, trim whitespace.
