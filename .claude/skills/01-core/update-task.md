---
name: update-task
description: Update an existing task. Use when user wants to modify task details.
---

When updating a task:

1. **Required**: user_id, task_id
2. **Optional fields**: title, description, status, priority, due_date
3. Only update provided fields, leave others unchanged.

Input:
```typescript
{ user_id, task_id, title?, description?, status?, priority?, due_date? }
```

Validate ownership - user can only update their own tasks.
