---
name: delete-task
description: Delete a task. Use when user wants to remove a task.
---

When deleting a task:

1. **Required**: user_id, task_id
2. **Requires confirmation**: confirm=true
3. Permanent deletion - cannot be undone

Input:
```typescript
{ user_id, task_id, confirm: true }
```

Validate ownership - user can only delete their own tasks.
