---
name: extract-intent
description: Extract user intent from natural language. Use for chatbot message parsing.
---

When extracting intent:

1. Analyze user's message
2. Identify intent: create_task, list_tasks, update_task, delete_task, complete_task, search_tasks, help, greeting
3. Extract entities: task_id, title, description, priority, due_date

Common patterns:
- "add task" → create_task
- "show my tasks" → list_tasks
- "complete task 1" → complete_task
- "delete the first one" → delete_task
- "find tasks about groceries" → search_tasks
