---
name: list-tasks
description: List user's tasks with optional filtering. Use when showing tasks to user.
---

When listing tasks:

1. **Required**: user_id
2. **Optional filters**: status (pending/completed/all), priority (low/medium/high)
3. **Pagination**: limit (1-100, default 20), offset

Input:
```typescript
{ user_id, status?, priority?, limit?, offset? }
```

Returns array of tasks sorted by created_at desc.
