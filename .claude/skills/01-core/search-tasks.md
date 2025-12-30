---
name: search-tasks
description: Search tasks by keyword. Use when user searches for tasks.
---

When searching tasks:

1. **Required**: user_id, query (search term)
2. **Optional**: status, priority, due_before, due_after
3. **Pagination**: page, limit (max 100)

Input:
```typescript
{ user_id, query, status?, priority?, page?, limit? }
```

Searches title and description fields.
