# Chatbot Feature Specification

## 🎯 Overview

This document specifies the conversational interface features for the AI-powered todo management chatbot. The chatbot enables users to manage their todos through natural language conversation.

---

## 📋 Feature Requirements

### Core Conversational Capabilities

The chatbot must understand and respond to natural language requests for:
1. Creating todos
2. Listing/viewing todos
3. Updating todos
4. Completing todos
5. Deleting todos
6. Searching todos
7. Filtering todos

---

## 1️⃣ Feature: Create Todos via Natural Language

### User Stories

**US-3.1.1:** As a user, I want to create a todo by describing it naturally, so I don't have to fill out a form.

**Acceptance Criteria:**
- User can say "Add buy groceries to my list" → Creates todo with title "Buy groceries"
- User can say "I need to finish the report by Friday" → Creates todo with title "Finish the report" and due date set to next Friday
- User can say "Remind me to call mom tomorrow, high priority" → Creates todo with priority "high" and due date tomorrow
- System confirms creation with details shown back to user
- System asks clarifying questions if information is ambiguous

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "Add buy milk" | create_todo | title: "Buy milk" |
| "I need to buy groceries tomorrow" | create_todo | title: "Buy groceries", due_date: tomorrow |
| "Create a high priority task to finish report" | create_todo | title: "Finish report", priority: "high" |
| "Remind me to call dentist on Monday" | create_todo | title: "Call dentist", due_date: next Monday |
| "Add task: review PRs. Description: check all pending code reviews" | create_todo | title: "Review PRs", description: "Check all pending code reviews" |

### Conversation Flow Example

```
User: "I need to buy groceries tomorrow"

AI: "I've created a todo for you:
     📝 Buy groceries
     📅 Due: Tomorrow (Dec 19, 2025)

     Would you like to add any details or set a priority?"

User: "Make it high priority"

AI: "Updated! 'Buy groceries' is now set to high priority."
```

### Edge Cases

1. **Ambiguous dates:** "I need to finish this next week"
   - AI asks: "Which day next week would you like this due?"

2. **Multiple tasks in one message:** "I need to buy milk and call the dentist"
   - AI asks: "I see two tasks. Should I create them separately?"

3. **Missing title:** "Add a task for tomorrow"
   - AI asks: "What would you like the task to be?"

### MCP Tool Used
- `create_todo`

---

## 2️⃣ Feature: List and View Todos

### User Stories

**US-3.2.1:** As a user, I want to ask what tasks I have, so I can see my todo list conversationally.

**Acceptance Criteria:**
- User can say "What do I need to do?" → Shows all pending todos
- User can say "Show me today's tasks" → Shows todos due today
- User can say "What's on my list?" → Shows all todos with status
- System presents todos in a readable format with numbering
- System includes relevant details (priority, due date, status)

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "What do I need to do?" | list_todos | status: "pending" |
| "Show my tasks" | list_todos | status: "all" |
| "What's due today?" | list_todos | due_date: today |
| "Show completed tasks" | list_todos | status: "completed" |
| "What are my high priority tasks?" | list_todos | priority: "high" |
| "Show me everything" | list_todos | status: "all" |

### Conversation Flow Example

```
User: "What do I need to do today?"

AI: "You have 3 tasks due today:

     1. 🔴 Buy groceries (High priority)
        Due: Today

     2. 📞 Call dentist
        Due: Today

     3. 📄 Review meeting notes (Low priority)
        Due: Today

     Would you like details on any of these?"

User: "Tell me about number 3"

AI: "Here are the details for 'Review meeting notes':

     📝 Title: Review meeting notes
     📋 Description: Check action items from yesterday's standup
     ⏰ Due: Today (Dec 18, 2025)
     🎯 Priority: Low
     ✅ Status: Pending

     Would you like to update anything?"
```

### Display Formats

**List View (Multiple Todos):**
```
You have 3 pending tasks:

1. 🔴 Buy groceries (High priority, due today)
2. 📞 Call dentist (Due tomorrow)
3. 📄 Finish report (Due next week)
```

**Detail View (Single Todo):**
```
📝 Buy groceries
📋 Get milk, eggs, bread, and vegetables
⏰ Due: Today (Dec 18, 2025) at 5:00 PM
🎯 Priority: High
✅ Status: Pending
📅 Created: Dec 17, 2025
```

**Empty State:**
```
You don't have any pending tasks. Great job staying on top of things! 🎉

Would you like to add a new task?
```

### Edge Cases

1. **Too many results:** If >10 todos, paginate or summarize
   - "You have 25 pending tasks. Here are the 5 most urgent..."

2. **No results for filter:** "Show high priority tasks" but none exist
   - "You don't have any high priority tasks right now."

3. **Overdue tasks:** Highlight with special indicator
   - "⚠️ Buy groceries (OVERDUE - was due yesterday)"

### MCP Tool Used
- `list_todos`
- `search_todos` (for filtered queries)

---

## 3️⃣ Feature: Update Todos

### User Stories

**US-3.3.1:** As a user, I want to modify my todos through conversation, so I can easily make changes.

**Acceptance Criteria:**
- User can say "Change the groceries task to tomorrow" → Updates due date
- User can say "Make the report task high priority" → Updates priority
- User can say "Update task 2 description to include meeting prep" → Updates description
- System identifies the correct todo even with partial information
- System confirms the update

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "Change buy groceries to tomorrow" | update_todo | title match: "buy groceries", due_date: tomorrow |
| "Make the report high priority" | update_todo | title match: "report", priority: "high" |
| "Update task 1 to be due next Monday" | update_todo | task_number: 1, due_date: next Monday |
| "Rename 'call dentist' to 'dentist appointment 2pm'" | update_todo | old_title: "call dentist", new_title: "dentist appointment 2pm" |
| "Move all today's tasks to tomorrow" | update_todo (batch) | due_date: today → tomorrow |

### Conversation Flow Example

```
User: "Change the groceries task to tomorrow"

AI: "I found 'Buy groceries' (currently due today).
     Would you like me to move it to tomorrow?"

User: "Yes"

AI: "Done! 'Buy groceries' is now due tomorrow (Dec 19, 2025)."
```

### Ambiguity Resolution

```
User: "Make the meeting task high priority"

AI: "I found 2 tasks related to 'meeting':
     1. Review meeting notes
     2. Prepare for meeting with client

     Which one would you like to update?"

User: "The first one"

AI: "Updated! 'Review meeting notes' is now high priority."
```

### Supported Update Operations

| Field | Update Examples |
|-------|----------------|
| **Title** | "Rename X to Y", "Change title of X" |
| **Description** | "Add description to X: ...", "Update notes for X" |
| **Due Date** | "Move X to tomorrow", "Change X deadline to Friday" |
| **Priority** | "Make X high priority", "Set X to low priority" |
| **Status** | "Mark X as complete" (see Feature 4) |

### Edge Cases

1. **Multiple matches:** "Update the task"
   - AI lists all tasks and asks which one

2. **Invalid update:** "Change due date to yesterday"
   - AI warns: "That date is in the past. Did you mean to mark it complete?"

3. **No matches:** "Update the cooking task"
   - AI responds: "I couldn't find a task about cooking. Would you like to create one?"

### MCP Tool Used
- `update_todo`
- `search_todos` (for finding the right todo)

---

## 4️⃣ Feature: Complete Todos

### User Stories

**US-3.4.1:** As a user, I want to mark tasks as done through conversation, so I can track my progress naturally.

**Acceptance Criteria:**
- User can say "I finished buying groceries" → Marks todo as completed
- User can say "Mark task 1 as done" → Updates status to completed
- User can say "Check off the dentist appointment" → Completes the task
- System provides positive reinforcement
- System shows remaining task count

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "I finished buying groceries" | update_todo | title match: "groceries", status: "completed" |
| "Mark task 1 as done" | update_todo | task_number: 1, status: "completed" |
| "Complete the report" | update_todo | title match: "report", status: "completed" |
| "Check off dentist" | update_todo | title match: "dentist", status: "completed" |
| "I did all of today's tasks" | update_todo (batch) | due_date: today, status: "completed" |

### Conversation Flow Example

```
User: "I finished buying groceries"

AI: "Awesome! 🎉 I've marked 'Buy groceries' as completed.

     You have 2 tasks remaining for today. Keep it up!"
```

### Completion Confirmation Variations

- "Great work! ✅ 'X' is now complete."
- "Nicely done! 🎉 'X' has been checked off your list."
- "Excellent! 👏 'X' is marked as done."
- "Way to go! 🌟 'X' is completed."

### Batch Completion

```
User: "I finished all of today's tasks"

AI: "Amazing! 🎉 I've marked 3 tasks as completed:
     ✅ Buy groceries
     ✅ Call dentist
     ✅ Review meeting notes

     You're all caught up for today! 🌟"
```

### Edge Cases

1. **Already completed:** "Mark groceries as done" (already done)
   - AI: "'Buy groceries' is already marked as complete. Good catch!"

2. **Ambiguous reference:** "I finished it"
   - AI: "Which task did you finish?"

3. **Undo completion:** "Actually, I didn't finish the report yet"
   - AI: "No problem! I've marked 'Finish report' as pending again."

### MCP Tool Used
- `update_todo` (status: "completed")

---

## 5️⃣ Feature: Delete Todos

### User Stories

**US-3.5.1:** As a user, I want to remove tasks I no longer need, so my list stays relevant.

**Acceptance Criteria:**
- User can say "Delete the groceries task" → Removes todo
- User can say "Remove task 2" → Deletes specified todo
- System asks for confirmation before deleting
- System provides confirmation after deletion

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "Delete the groceries task" | delete_todo | title match: "groceries" |
| "Remove task 2" | delete_todo | task_number: 2 |
| "Get rid of the meeting task" | delete_todo | title match: "meeting" |
| "Cancel the dentist appointment task" | delete_todo | title match: "dentist" |
| "Clear all completed tasks" | delete_todo (batch) | status: "completed" |

### Conversation Flow Example

```
User: "Delete the groceries task"

AI: "Are you sure you want to delete 'Buy groceries'?
     This action cannot be undone."

User: "Yes, delete it"

AI: "Done! 'Buy groceries' has been removed from your list."
```

### Safety Confirmations

**Single Delete:**
```
AI: "⚠️ Are you sure you want to delete 'Buy groceries'?

     Type 'yes' to confirm or 'no' to cancel."
```

**Batch Delete:**
```
User: "Delete all completed tasks"

AI: "⚠️ This will permanently delete 5 completed tasks:
     1. Buy groceries
     2. Call dentist
     3. Review notes
     4. Send email
     5. Update calendar

     Are you sure? Type 'yes' to confirm."
```

### Edge Cases

1. **No match found:** "Delete the cooking task" (doesn't exist)
   - AI: "I couldn't find a task about cooking. Would you like to see all your tasks?"

2. **Accidental deletion:** User wants to restore
   - Implement undo within conversation context
   - AI: "I've deleted 'X'. If this was a mistake, say 'undo' within the next minute."

3. **Multiple matches:** "Delete the meeting task"
   - AI lists matches and asks which one to delete

### MCP Tool Used
- `delete_todo`
- `search_todos` (for finding the right todo)

---

## 6️⃣ Feature: Search Todos

### User Stories

**US-3.6.1:** As a user, I want to find specific tasks by keyword, so I can quickly locate what I need.

**Acceptance Criteria:**
- User can say "Find tasks about groceries" → Returns matching todos
- User can say "Search for work tasks" → Shows work-related todos
- User can say "What tasks mention the client meeting?" → Finds related tasks
- System searches title and description fields
- System highlights matching terms in results

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Parameters |
|-------------------|------------------|------------|
| "Find tasks about groceries" | search_todos | query: "groceries" |
| "Search for work" | search_todos | query: "work" |
| "What tasks mention meeting?" | search_todos | query: "meeting" |
| "Show me everything with 'urgent'" | search_todos | query: "urgent" |
| "Find my client tasks" | search_todos | query: "client" |

### Conversation Flow Example

```
User: "Find tasks about meetings"

AI: "I found 3 tasks matching 'meetings':

     1. 📄 Review meeting notes
        Due: Today
        Description: Check action items from yesterday's standup

     2. 📅 Prepare for client meeting
        Due: Tomorrow (High priority)

     3. 📧 Send meeting agenda
        Due: Next Monday

     Would you like details on any of these?"
```

### Search Result Display

**With matches:**
```
Found 2 tasks matching "report":

1. 📄 Finish quarterly report (High priority, due Friday)
   Description: Complete financial analysis and executive summary

2. 📊 Review team performance reports (Due next week)
   Description: Analyze Q4 performance metrics

Would you like to update or complete any of these?
```

**No matches:**
```
I couldn't find any tasks matching "vacation".

Your current pending tasks are:
1. Buy groceries
2. Call dentist
3. Finish report

Would you like to create a new task about vacation?
```

### Advanced Search

User can combine search with filters:
- "Find high priority tasks about work"
- "Search completed tasks for project X"
- "Show me overdue tasks with 'client' in them"

### Edge Cases

1. **Too many results:** >10 matches
   - AI: "I found 15 tasks matching 'work'. Here are the 5 most recent..."

2. **Empty search:** "Find tasks"
   - AI: "What would you like to search for?"

3. **Similar terms:** Search "shopping" finds "groceries"
   - Use semantic search or suggest: "Did you mean 'groceries'?"

### MCP Tool Used
- `search_todos`

---

## 7️⃣ Feature: Filter and Sort Todos

### User Stories

**US-3.7.1:** As a user, I want to filter my tasks by various criteria, so I can focus on what matters.

**Acceptance Criteria:**
- User can say "Show high priority tasks" → Filters by priority
- User can say "What's due this week?" → Filters by due date range
- User can say "Show completed tasks" → Filters by status
- System can combine multiple filters
- System explains the applied filters

### Natural Language Patterns to Support

| User Input Example | Extracted Intent | Filters Applied |
|-------------------|------------------|-----------------|
| "Show high priority tasks" | list_todos | priority: "high" |
| "What's due today?" | list_todos | due_date: today |
| "Show completed tasks" | list_todos | status: "completed" |
| "What's overdue?" | list_todos | due_date: < today, status: "pending" |
| "Show me everything due this week" | list_todos | due_date: this_week |

### Conversation Flow Example

```
User: "Show me high priority tasks due this week"

AI: "Here are your high priority tasks due this week:

     🔴 Finish quarterly report
        Due: Friday (2 days away)

     🔴 Client presentation
        Due: Next Monday (4 days away)

     You have 2 high priority tasks this week.
     Need to adjust any deadlines?"
```

### Supported Filters

| Filter Type | Values | Examples |
|------------|--------|----------|
| **Status** | pending, completed, all | "Show completed tasks" |
| **Priority** | low, medium, high | "High priority items" |
| **Due Date** | today, tomorrow, this week, next week, overdue | "What's due today?" |
| **Time Range** | Relative or absolute dates | "Tasks between Monday and Friday" |

### Combined Filters

```
User: "Show me incomplete high priority tasks due this week"

AI: "Filtering by:
     ✓ Status: Pending
     ✓ Priority: High
     ✓ Due: This week

     Found 2 tasks:

     1. 🔴 Finish quarterly report (Due Friday)
     2. 🔴 Client presentation (Due Monday)

     Would you like to focus on one of these?"
```

### Sorting

Users can request sorted results:
- "Show tasks sorted by due date"
- "List tasks by priority"
- "Show oldest tasks first"

Default sort: Due date (ascending), then priority (high→low)

### Edge Cases

1. **No results for filter:** "Show low priority tasks" (none exist)
   - AI: "You don't have any low priority tasks right now."

2. **Conflicting filters:** "Show completed tasks that are overdue"
   - AI: "Completed tasks can't be overdue. Did you mean pending tasks?"

3. **Unclear time range:** "Show tasks for soon"
   - AI: "By 'soon', do you mean today, this week, or something else?"

### MCP Tool Used
- `list_todos` (with filter parameters)

---

## 8️⃣ Feature: Context and Memory

### User Stories

**US-3.8.1:** As a user, I want the chatbot to remember our conversation, so I don't have to repeat myself.

**Acceptance Criteria:**
- Chatbot remembers previous messages in the session
- User can refer to tasks by context ("that one", "the first task")
- Chatbot references earlier conversation appropriately
- Context persists across page reloads (via session_id)

### Context Examples

**Reference by position:**
```
User: "Show my tasks"
AI: [Lists 3 tasks]

User: "Make the second one high priority"
AI: "I've updated 'Call dentist' to high priority."
```

**Reference by description:**
```
User: "What's due today?"
AI: "You have 'Buy groceries' due today."

User: "Mark it as done"
AI: "Great! 'Buy groceries' is now complete."
```

**Follow-up questions:**
```
User: "Create a task to buy groceries"
AI: "I've created 'Buy groceries'. Would you like to set a due date?"

User: "Yes, tomorrow"
AI: "Done! 'Buy groceries' is now due tomorrow."
```

### Context Retention

**Short-term (Session):**
- Last 10-20 messages
- Recently mentioned tasks
- Active task being discussed
- Current filter/search context

**Long-term (Database):**
- Full conversation history per session_id
- User preferences (if any)
- Recurring patterns (future enhancement)

### Conversation Continuity

```
User: "Show my tasks"
[User closes browser]
[User opens browser again, same session_id]

User: "Add another one"
AI: "Sure! What task would you like to add to your list?"
```

### Edge Cases

1. **Ambiguous reference:** "Delete that one"
   - AI: "Which task would you like to delete? Could you be more specific?"

2. **Context expired:** Reference task from 100 messages ago
   - AI: "I'm not sure which task you're referring to. Could you describe it?"

3. **New session:** User starts fresh conversation
   - AI: "Hello! I'm your todo assistant. How can I help you today?"

### MCP Tool Used
- All tools (context helps identify correct todo)
- Backend loads chat history from `ChatHistory` table

---

## 9️⃣ Feature: Error Handling and Help

### User Stories

**US-3.9.1:** As a user, I want helpful error messages when something goes wrong, so I know what to do.

**Acceptance Criteria:**
- System provides clear error messages
- System suggests how to fix errors
- System offers help when user is stuck
- System handles unexpected input gracefully

### Error Scenarios

**1. Task Not Found:**
```
User: "Delete the cooking task"

AI: "I couldn't find a task about cooking in your list.

     Would you like to:
     - See all your tasks
     - Create a new task
     - Search for something else"
```

**2. Invalid Date:**
```
User: "Set due date to yesterday"

AI: "That date is in the past. Tasks should have future due dates.

     Did you mean to:
     - Mark the task as complete?
     - Set it for today or tomorrow?"
```

**3. Missing Information:**
```
User: "Create a task"

AI: "I'd be happy to create a task for you!
     What would you like the task to be?"
```

**4. System Error:**
```
AI: "I'm sorry, I encountered an error while updating your task.
     Please try again in a moment. If the problem persists,
     your todo list is safe and you can refresh the page."
```

### Help Commands

User can request help:
- "Help"
- "What can you do?"
- "How do I...?"
- "Commands"

**Help Response:**
```
User: "Help"

AI: "I'm your AI todo assistant! Here's what I can help you with:

     ✅ Create tasks: 'Add buy milk', 'I need to call mom tomorrow'
     📋 View tasks: 'Show my tasks', 'What's due today?'
     ✏️ Update tasks: 'Make X high priority', 'Move X to tomorrow'
     ✔️ Complete tasks: 'I finished X', 'Mark X as done'
     🗑️ Delete tasks: 'Delete X', 'Remove task 2'
     🔍 Search tasks: 'Find tasks about X'

     Just tell me what you need in your own words!"
```

### Unrecognized Input

```
User: "xyzabc123"

AI: "I'm not sure what you mean. Could you rephrase that?

     If you're trying to:
     - Add a task: Say 'Add [task name]'
     - View tasks: Say 'Show my tasks'
     - Get help: Say 'Help'

     What would you like to do?"
```

### Edge Cases

1. **Empty input:** User sends blank message
   - AI: "Did you mean to send something? Let me know how I can help!"

2. **Very long input:** >500 words
   - AI: "That's a lot of information! Could you break that into separate tasks?"

3. **Inappropriate content:** User sends offensive text
   - AI: "I'm here to help with your todo list. Please keep the conversation professional."

### MCP Tool Used
- No specific tool (error handling at AI agent level)

---

## 🎨 Conversation Design Principles

### 1. Natural and Friendly
- Use conversational language, not robotic responses
- Include appropriate emojis for visual appeal
- Vary responses to avoid repetition

### 2. Clear and Concise
- Get to the point quickly
- Use formatting (bullets, numbers) for readability
- Highlight important information

### 3. Proactive and Helpful
- Suggest next actions
- Offer assistance before user asks
- Provide context-aware recommendations

### 4. Forgiving and Flexible
- Accept multiple phrasings for same intent
- Handle typos and grammatical errors
- Allow users to change their mind

### 5. Transparent and Trustworthy
- Confirm actions before executing (especially deletes)
- Show what was changed
- Admit when uncertain and ask for clarification

---

## 📊 Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Intent Recognition Accuracy | >90% | Correct tool selection rate |
| Task Completion Rate | >95% | Successfully executed operations |
| Average Response Time | <2s | Time from user message to AI response |
| Error Recovery Rate | >80% | User successfully retries after error |
| User Satisfaction | >4/5 | Post-interaction rating (future) |

---

## 🔄 Conversation State Machine

```
[Start] → Welcome Message
   ↓
[Listening] → User Input
   ↓
[Processing] → Intent Recognition
   ↓
   ├─→ [Execute Tool] → Confirmation → [Listening]
   ├─→ [Clarify] → Follow-up Question → [Listening]
   └─→ [Error] → Error Message → [Listening]
```

---

## 🚀 Implementation Priority

### Phase 1 (MVP)
1. Create todos (US-3.1.1)
2. List todos (US-3.2.1)
3. Complete todos (US-3.4.1)
4. Basic error handling (US-3.9.1)

### Phase 2 (Enhanced)
5. Update todos (US-3.3.1)
6. Delete todos (US-3.5.1)
7. Search todos (US-3.6.1)

### Phase 3 (Advanced)
8. Filter and sort (US-3.7.1)
9. Context and memory (US-3.8.1)
10. Advanced help system

---

## 🧪 Testing Scenarios

### Test Case 1: Simple Create
```
Input: "Add buy milk"
Expected: Todo created with title "Buy milk"
Verify: list_todos shows new todo
```

### Test Case 2: Complex Create
```
Input: "I need to finish the quarterly report by Friday, high priority"
Expected: Todo created with:
  - title: "Finish the quarterly report"
  - due_date: next Friday
  - priority: "high"
```

### Test Case 3: Ambiguous Reference
```
Input: "Show my tasks"
Output: [3 tasks listed]
Input: "Complete the first one"
Expected: Task 1 marked as completed
```

### Test Case 4: Error Recovery
```
Input: "Delete the cooking task"
Output: "Task not found"
Input: "Show all tasks"
Expected: Lists all tasks
```

### Test Case 5: Multi-turn Conversation
```
Input: "Add buy groceries"
Output: "Created 'Buy groceries'"
Input: "Make it due tomorrow"
Output: "Updated due date to tomorrow"
Input: "And high priority"
Output: "Set to high priority"
```

---

## 📝 Notes

- All features must maintain stateless design
- Conversation state loaded from database per request
- MCP tools handle all database operations
- AI agent makes decisions, MCP tools execute
- Better Auth provides user_id for all operations
- Session continuity via session_id in ChatHistory table

---

## 🔗 Related Specifications

- [overview.md](../overview.md) - Overall project specification
- [agents/todo-agent.md](../agents/todo-agent.md) - AI agent behavior
- [api/mcp-tools.md](../api/mcp-tools.md) - MCP tool definitions
- [database/chat-history.md](../database/chat-history.md) - Conversation persistence

---

**Status:** Draft - Ready for Review
**Last Updated:** 2025-12-18
