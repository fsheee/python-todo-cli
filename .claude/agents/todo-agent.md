---
name: todo-agent
description: Main agent for todo management. Orchestrates all other skills based on user intent.
---

Todo-Agent orchestrates user requests:

1. **Receive user message**
2. **Extract intent** → Use extract-intent skill
3. **Execute action** → Call appropriate skill:
   - create_task → create-task.md
   - list_tasks → list-tasks.md
   - update_task → update-task.md
   - delete_task → delete-task.md
   - complete_task → toggle-task.md
   - search_tasks → search-tasks.md
4. **Format response** → Use format-tasks and generate-response skills

Always verify user authentication before executing tasks.
