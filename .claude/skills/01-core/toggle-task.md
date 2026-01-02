---
name: toggle-task
description: Toggle task completion status. Use when user marks task as done/undone.
---

When toggling task:

1. **Required**: user_id, task_id
2. Switches status: pending ↔ completed
3. Sets completed_at timestamp when marking complete

Input:
```typescript
{ user_id, task_id }
```

Returns updated task with new status and completed_at.
