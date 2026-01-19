# Phase 3 Implementation Plan

## 🎯 Overview

This document expands all Phase 3 specifications into detailed, testable implementation plans. It defines all agent ↔ MCP tool ↔ backend interactions without generating code.

**Status:** Ready for task breakdown and implementation via Claude Code.

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Feature Implementation Plans](#feature-implementation-plans)
3. [Agent Implementation Plan](#agent-implementation-plan)
4. [MCP Tools Implementation Plan](#mcp-tools-implementation-plan)
5. [Database Implementation Plan](#database-implementation-plan)
6. [UI Implementation Plan](#ui-implementation-plan)
7. [Integration Points](#integration-points)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Plan](#deployment-plan)

---

## 🏗 Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    User (Browser)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Frontend (React + OpenAI ChatKit)                  │
│  - Authentication (JWT storage)                                 │
│  - Session management (localStorage)                            │
│  - Chat UI rendering                                            │
│  - API communication                                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ POST /chat (JWT in header)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend Server                         │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Chat Endpoint (/chat)                                 │    │
│  │  1. Validate JWT → Extract user_id                     │    │
│  │  2. Load chat history from DB                          │    │
│  │  3. Build agent context                                │    │
│  │  4. Call OpenAI Agent                                  │    │
│  │  5. Save messages to DB                                │    │
│  │  6. Return response                                    │    │
│  └────────────────────────┬───────────────────────────────┘    │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────┐    │
│  │  Better Auth Middleware                                │    │
│  │  - JWT validation                                      │    │
│  │  - User context injection                              │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Agent invocation
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              OpenAI Agent (Todo Assistant)                      │
│  - System prompt + context                                      │
│  - Intent recognition                                           │
│  - Tool selection logic                                         │
│  - Response generation                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP tool calls
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Server                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  5 MCP Tools:                                            │  │
│  │  - create_todo(user_id, title, ...)                     │  │
│  │  - list_todos(user_id, filters, ...)                    │  │
│  │  - update_todo(user_id, todo_id, ...)                   │  │
│  │  - delete_todo(user_id, todo_id, confirm)               │  │
│  │  - search_todos(user_id, query, ...)                    │  │
│  └────────────────────────┬─────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            │ HTTP calls to Phase 2
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              Phase 2 Backend (CRUD Endpoints)                   │
│  - POST /todos                                                  │
│  - GET /todos?user_id=X&filters...                             │
│  - PUT /todos/{id}                                              │
│  - DELETE /todos/{id}                                           │
│  - GET /todos/search?q=...                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ SQLModel queries
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Neon PostgreSQL Database                           │
│  Tables:                                                        │
│  - users (Phase 2)                                              │
│  - todos (Phase 2)                                              │
│  - chat_history (Phase 3 - NEW)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Key Interaction Flows

**Flow 1: User sends message "Add buy milk"**
```
1. Frontend → POST /chat
   Headers: Authorization: Bearer {jwt}
   Body: { message: "Add buy milk", session_id: "sess_123" }

2. Backend /chat endpoint:
   a. Validate JWT → Extract user_id=123
   b. Load history: SELECT * FROM chat_history WHERE user_id=123 AND session_id='sess_123'
   c. Save user message: INSERT INTO chat_history (user_id, session_id, role='user', content='Add buy milk')

3. Backend → OpenAI Agent:
   Input: { user_id: 123, history: [...], message: "Add buy milk" }
   Agent recognizes: Intent=CREATE_TODO, params={title: "Buy milk"}
   Agent calls: create_todo tool

4. MCP create_todo tool:
   a. Validate inputs
   b. HTTP POST to Phase 2: /todos with {user_id: 123, title: "Buy milk"}
   c. Phase 2 → INSERT INTO todos (user_id, title, status) VALUES (123, 'Buy milk', 'pending')
   d. Phase 2 returns: {id: 456, title: "Buy milk", status: "pending"}
   e. MCP tool returns: {success: true, todo: {...}}

5. Agent generates response: "I've added 'Buy milk' to your list. 📝"

6. Backend:
   a. Save assistant message: INSERT INTO chat_history (user_id, session_id, role='assistant', content='...')
   b. Return to frontend: {response: "I've added 'Buy milk'...", session_id: "sess_123"}

7. Frontend: Display message in ChatKit UI
```

**Flow 2: User sends message "Show my tasks"**
```
1. Frontend → POST /chat (same as above)

2. Backend validates JWT, loads history, saves user message

3. Agent recognizes: Intent=LIST_TODOS
   Agent calls: list_todos tool

4. MCP list_todos tool:
   a. HTTP GET to Phase 2: /todos?user_id=123&status=pending
   b. Phase 2 → SELECT * FROM todos WHERE user_id=123 AND status='pending'
   c. Phase 2 returns: [{id: 456, title: "Buy milk"}, ...]
   d. MCP tool returns: {success: true, todos: [...], count: 3}

5. Agent formats response:
   "You have 3 pending tasks:
   1. 📝 Buy milk
   2. 📞 Call dentist
   ..."

6. Backend saves assistant message and returns to frontend

7. Frontend displays formatted list
```

---

## 📋 Feature Implementation Plans

### Feature 1: Create Todos via Natural Language

**Spec Reference:** `specs/features/chatbot.md` - Section 1

**User Stories:**
- US-3.1.1: Create todo by describing naturally

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: User message (e.g., "Add buy milk")
   - Output: Intent=CREATE_TODO, parameters extracted
   - Logic: Pattern matching + OpenAI function calling
   - Test: 20+ variations of create requests

2. **Parameter Extraction**
   - Extract: title (required)
   - Extract: description (optional)
   - Extract: due_date (optional, parse natural language dates)
   - Extract: priority (optional, recognize "high/medium/low")
   - Test: Complex sentences with multiple parameters

3. **MCP Tool Call**
   - Tool: `create_todo`
   - Parameters: user_id, title, description?, due_date?, priority?
   - Validation: title non-empty, max 200 chars
   - Test: Valid and invalid inputs

4. **Phase 2 Backend Call**
   - Endpoint: POST /todos
   - Body: {user_id, title, description, priority, due_date, status="pending"}
   - Response: Created todo with ID
   - Test: Database insertion verified

5. **Response Generation**
   - Format: "I've created a new todo: {title} ..."
   - Include: Confirmation + details
   - Ask: Follow-up questions if needed
   - Test: Response clarity and helpfulness

**Acceptance Criteria:**
- ✅ User can create todo with just title
- ✅ User can specify due date in natural language
- ✅ User can set priority (high/medium/low)
- ✅ Agent asks clarifying questions for ambiguous dates
- ✅ Database record created with correct user_id
- ✅ Confirmation message displayed to user

**Test Cases:**
```
TC-1.1: Simple create
Input: "Add buy milk"
Expected: Todo created with title="Buy milk", status="pending"

TC-1.2: Create with due date
Input: "I need to finish report by Friday"
Expected: Todo created with due_date=next_friday

TC-1.3: Create with priority
Input: "Add high priority task to call client"
Expected: Todo created with priority="high"

TC-1.4: Ambiguous date
Input: "Add task for next week"
Expected: Agent asks "Which day next week?"

TC-1.5: Empty title
Input: "Add a task"
Expected: Agent asks "What would you like the task to be?"
```

---

### Feature 2: List and View Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 2

**User Stories:**
- US-3.2.1: Ask what tasks I have

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "What do I need to do?", "Show my tasks"
   - Output: Intent=LIST_TODOS, filters extracted
   - Filters: status (pending/completed/all), due_date, priority
   - Test: Various list requests

2. **Filter Extraction**
   - Due date filters: today, tomorrow, this week, overdue
   - Priority filters: high, medium, low
   - Status filters: pending, completed, all
   - Test: Combining multiple filters

3. **MCP Tool Call**
   - Tool: `list_todos`
   - Parameters: user_id, status?, priority?, due_date_range?
   - Validation: Valid enum values
   - Test: All filter combinations

4. **Phase 2 Backend Call**
   - Endpoint: GET /todos?user_id=X&filters...
   - Query: SELECT with WHERE clauses
   - Response: Array of todos
   - Test: Correct filtering in database

5. **Response Formatting**
   - Format: Numbered list with emojis
   - Include: Priority indicators, due dates, status
   - Pagination: Limit to 10 items, offer "show more"
   - Test: Readable and clear formatting

**Acceptance Criteria:**
- ✅ User can list all pending todos
- ✅ User can filter by due date (today, this week, etc.)
- ✅ User can filter by priority
- ✅ User can see completed todos
- ✅ Empty state message when no todos
- ✅ Overdue tasks highlighted

**Test Cases:**
```
TC-2.1: List all pending
Input: "Show my tasks"
Expected: List of pending todos with details

TC-2.2: Filter by due date
Input: "What's due today?"
Expected: Only todos with due_date=today

TC-2.3: Filter by priority
Input: "Show high priority tasks"
Expected: Only todos with priority="high"

TC-2.4: Empty state
Input: "Show completed tasks" (when none exist)
Expected: "You don't have any completed tasks"

TC-2.5: Overdue tasks
Input: "What's overdue?"
Expected: Tasks with due_date < today and status="pending"
```

---

### Feature 3: Update Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 3

**User Stories:**
- US-3.3.1: Modify todos through conversation

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "Change X to Y", "Make X high priority"
   - Output: Intent=UPDATE_TODO, todo_identifier, field, new_value
   - Todo identification: By title match, by number from list
   - Test: Various update request formats

2. **Todo Resolution**
   - If title match: Search for todo by title (may need disambiguation)
   - If number reference: Use from context (last list)
   - Multiple matches: Ask user to clarify
   - Test: Ambiguity handling

3. **MCP Tool Calls**
   - First: `search_todos` (if needed to identify todo)
   - Then: `update_todo` with todo_id and fields to update
   - Validation: At least one field to update
   - Test: All updatable fields

4. **Phase 2 Backend Call**
   - Endpoint: PUT /todos/{id}
   - Body: {user_id, field_updates}
   - Response: Updated todo
   - Test: Database record updated

5. **Response Generation**
   - Format: "Updated! {title} is now {change}"
   - Confirmation: Show what changed
   - Test: Clear confirmation messages

**Acceptance Criteria:**
- ✅ User can update title
- ✅ User can update description
- ✅ User can update due date
- ✅ User can update priority
- ✅ Agent handles ambiguous references
- ✅ Agent confirms changes

**Test Cases:**
```
TC-3.1: Update due date
Input: "Change groceries to tomorrow"
Expected: todo.due_date updated to tomorrow

TC-3.2: Update priority
Input: "Make report high priority"
Expected: todo.priority updated to "high"

TC-3.3: Multiple matches
Input: "Update the meeting task"
Expected: Agent lists matching tasks, asks which one

TC-3.4: Update by number
Input: "Update task 2 to due next Monday"
Expected: Second task from last list updated

TC-3.5: No matches
Input: "Update cooking task"
Expected: "I couldn't find a task about cooking"
```

---

### Feature 4: Complete Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 4

**User Stories:**
- US-3.4.1: Mark tasks as done conversationally

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "I finished X", "Mark X as done"
   - Output: Intent=COMPLETE_TODO, todo_identifier
   - Same resolution logic as update
   - Test: Various completion phrases

2. **Todo Resolution**
   - Search by title or use context
   - Handle ambiguity
   - Test: All identification methods

3. **MCP Tool Call**
   - Tool: `update_todo`
   - Parameters: user_id, todo_id, status="completed"
   - Validation: Todo exists and belongs to user
   - Test: Status change in database

4. **Phase 2 Backend Call**
   - Endpoint: PUT /todos/{id}
   - Body: {user_id, status: "completed"}
   - Response: Updated todo
   - Test: Timestamp updated

5. **Response Generation**
   - Format: Positive reinforcement + remaining count
   - Variations: "Great work!", "Awesome!", "Nicely done!"
   - Show: Remaining task count
   - Test: Encouraging messages

**Acceptance Criteria:**
- ✅ User can mark single todo as complete
- ✅ User can mark multiple todos as complete
- ✅ Agent provides positive reinforcement
- ✅ Agent shows remaining task count
- ✅ User can undo completion
- ✅ Already completed todos handled gracefully

**Test Cases:**
```
TC-4.1: Simple completion
Input: "I finished buying groceries"
Expected: Todo status changed to "completed"

TC-4.2: Completion by number
Input: "Mark task 1 as done"
Expected: First task from list completed

TC-4.3: Batch completion
Input: "I finished all of today's tasks"
Expected: All tasks with due_date=today marked completed

TC-4.4: Already completed
Input: "Mark groceries as done" (already done)
Expected: "Groceries is already complete"

TC-4.5: Undo completion
Input: "Actually I didn't finish the report"
Expected: Status changed back to "pending"
```

---

### Feature 5: Delete Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 5

**User Stories:**
- US-3.5.1: Remove tasks I no longer need

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "Delete X", "Remove task 2"
   - Output: Intent=DELETE_TODO, todo_identifier
   - Requires confirmation for safety
   - Test: Various delete requests

2. **Todo Resolution**
   - Search by title or use context
   - Must confirm before deletion
   - Test: Identification and confirmation flow

3. **Confirmation Flow**
   - Agent asks: "Are you sure? This cannot be undone"
   - Wait for user confirmation
   - If yes: proceed with deletion
   - If no: cancel operation
   - Test: Both paths

4. **MCP Tool Call**
   - Tool: `delete_todo`
   - Parameters: user_id, todo_id, confirm=true
   - Validation: Explicit confirmation required
   - Test: Confirmation enforcement

5. **Phase 2 Backend Call**
   - Endpoint: DELETE /todos/{id}?user_id=X
   - Response: Success confirmation
   - Database: Record deleted
   - Test: Todo removed from database

6. **Response Generation**
   - Format: "Done! {title} has been removed"
   - Safety: Always confirm before deletion
   - Test: Clear confirmation messages

**Acceptance Criteria:**
- ✅ User can delete single todo with confirmation
- ✅ User can batch delete with confirmation
- ✅ Agent always asks for confirmation
- ✅ User can cancel deletion
- ✅ Undo feature (within time window)
- ✅ Non-existent todo handled gracefully

**Test Cases:**
```
TC-5.1: Delete with confirmation
Input: "Delete groceries" → "Yes"
Expected: Todo deleted after confirmation

TC-5.2: Cancel deletion
Input: "Delete report" → "No"
Expected: Deletion cancelled

TC-5.3: Batch delete
Input: "Delete all completed tasks" → "Yes"
Expected: All completed todos deleted

TC-5.4: No match
Input: "Delete cooking task"
Expected: "I couldn't find that task"

TC-5.5: Undo delete
Input: "Undo" (within 1 minute)
Expected: Last deleted todo restored
```

---

### Feature 6: Search Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 6

**User Stories:**
- US-3.6.1: Find specific tasks by keyword

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "Find tasks about X", "Search for Y"
   - Output: Intent=SEARCH_TODOS, query
   - Extract: Search keywords
   - Test: Various search queries

2. **Query Extraction**
   - Extract: Main search terms
   - Handle: Multi-word queries
   - Filters: Can combine with status/priority
   - Test: Query parsing

3. **MCP Tool Call**
   - Tool: `search_todos`
   - Parameters: user_id, query, status?, limit
   - Validation: Non-empty query
   - Test: Search execution

4. **Phase 2 Backend Call**
   - Endpoint: GET /todos/search?q=X&user_id=Y
   - Query: Full-text search in title and description
   - Response: Matching todos with relevance score
   - Test: Search accuracy

5. **Response Formatting**
   - Format: Numbered list with highlights
   - Show: Match location (title vs description)
   - Empty: "No matches found" + suggestion
   - Test: Result presentation

**Acceptance Criteria:**
- ✅ User can search by keyword
- ✅ Search looks in title and description
- ✅ Results ranked by relevance
- ✅ User can combine search with filters
- ✅ No results handled with helpful message
- ✅ Similar terms suggested

**Test Cases:**
```
TC-6.1: Simple search
Input: "Find tasks about groceries"
Expected: Todos containing "groceries"

TC-6.2: Multi-word search
Input: "Search for client meeting"
Expected: Todos with both "client" and "meeting"

TC-6.3: No results
Input: "Find vacation tasks"
Expected: "No tasks found" + suggestion to create

TC-6.4: Search with filter
Input: "Find high priority work tasks"
Expected: High priority todos containing "work"

TC-6.5: Many results
Input: "Search for work" (15 matches)
Expected: Top 10 results + "show more" option
```

---

### Feature 7: Filter and Sort Todos

**Spec Reference:** `specs/features/chatbot.md` - Section 7

**User Stories:**
- US-3.7.1: Filter tasks by various criteria

**Implementation Steps:**

1. **Agent Intent Recognition**
   - Input: "Show high priority tasks", "What's due this week?"
   - Output: Intent=LIST_TODOS with filters
   - Extract: Multiple filter criteria
   - Test: Complex filter combinations

2. **Filter Extraction**
   - Status: pending/completed/all
   - Priority: low/medium/high
   - Due date: today/tomorrow/this_week/next_week/overdue
   - Combine: Multiple filters simultaneously
   - Test: All combinations

3. **MCP Tool Call**
   - Tool: `list_todos` with filter parameters
   - Validation: Valid filter values
   - Test: Filter application

4. **Phase 2 Backend Call**
   - Endpoint: GET /todos with query parameters
   - Query: Multiple WHERE clauses
   - Sort: By due_date, then priority
   - Test: Correct filtering and sorting

5. **Response Formatting**
   - Format: Filtered list with explanation
   - Show: What filters are applied
   - Count: Number of matching tasks
   - Test: Clear presentation

**Acceptance Criteria:**
- ✅ User can filter by status
- ✅ User can filter by priority
- ✅ User can filter by due date range
- ✅ User can combine multiple filters
- ✅ Results sorted logically
- ✅ Filter explanation shown

**Test Cases:**
```
TC-7.1: Single filter
Input: "Show high priority tasks"
Expected: Only priority="high" todos

TC-7.2: Date range filter
Input: "What's due this week?"
Expected: Todos with due_date in current week

TC-7.3: Combined filters
Input: "Show incomplete high priority tasks due this week"
Expected: status="pending" AND priority="high" AND due_date in week

TC-7.4: No results
Input: "Show low priority tasks" (none exist)
Expected: "You don't have any low priority tasks"

TC-7.5: Sort order
Input: "Show all tasks"
Expected: Sorted by due_date ascending, then priority descending
```

---

### Feature 8: Context and Memory

**Spec Reference:** `specs/features/chatbot.md` - Section 8

**User Stories:**
- US-3.8.1: Chatbot remembers conversation

**Implementation Steps:**

1. **Session Management**
   - Frontend: Generate session_id on first load
   - Storage: localStorage for persistence
   - Backend: Load history by session_id
   - Test: Session continuity

2. **History Loading**
   - Query: Load last 20 messages from chat_history table
   - Format: Array of {role, content, timestamp}
   - Context: Pass to agent with new message
   - Test: History retrieval

3. **Reference Resolution**
   - Numeric: "task 1", "the second one"
   - Pronoun: "it", "that one"
   - Descriptive: "the meeting task"
   - Context timeout: 5 messages for numbers, 3 for pronouns
   - Test: All reference types

4. **Context Building**
   - Agent receives: user_id, session_id, history, new message
   - Agent uses: History to resolve references
   - Agent maintains: Task list from last LIST_TODOS call
   - Test: Correct reference resolution

5. **Conversation Persistence**
   - Save: Every user and assistant message
   - Metadata: Include tool calls, timestamps
   - Retrieve: On session reload
   - Test: Persistence across page reloads

**Acceptance Criteria:**
- ✅ Agent remembers previous messages
- ✅ User can refer to "task 1" from list
- ✅ User can say "mark it done" about recent task
- ✅ Context persists across page reloads
- ✅ Context timeout handled gracefully
- ✅ New session clears context

**Test Cases:**
```
TC-8.1: Numeric reference
Input: "Show my tasks" → "Complete the first one"
Expected: First task from list marked complete

TC-8.2: Pronoun reference
Input: "Add buy milk" → "Make it high priority"
Expected: Just-created task updated to high priority

TC-8.3: Cross-session persistence
Input: "Show tasks" → [reload page] → "Add another"
Expected: Agent remembers it's adding to task list

TC-8.4: Context timeout
Input: "Show tasks" → [10 messages later] → "Complete number 1"
Expected: Agent asks "Which task?"

TC-8.5: New session
Input: Click "New Chat" → "Complete the first one"
Expected: Agent asks "Which task?" (no context)
```

---

### Feature 9: Error Handling and Help

**Spec Reference:** `specs/features/chatbot.md` - Section 9

**User Stories:**
- US-3.9.1: Helpful error messages

**Implementation Steps:**

1. **Error Detection**
   - Task not found
   - Invalid date
   - Missing information
   - System errors
   - Test: All error scenarios

2. **Error Response Generation**
   - Clear message explaining what went wrong
   - Helpful suggestions for recovery
   - Never expose technical details
   - Test: User-friendly messages

3. **Help System**
   - Commands: "help", "what can you do?"
   - Response: List of capabilities with examples
   - Context-sensitive: Offer relevant help
   - Test: Help clarity

4. **Fallback Handling**
   - Unrecognized input: Ask for clarification
   - Empty input: Prompt for input
   - Inappropriate content: Redirect professionally
   - Test: Edge cases

5. **Recovery Suggestions**
   - Always offer next steps
   - Provide examples
   - Link to related actions
   - Test: Helpfulness

**Acceptance Criteria:**
- ✅ Clear error messages
- ✅ Recovery suggestions provided
- ✅ Help command works
- ✅ Unrecognized input handled
- ✅ System errors don't expose internals
- ✅ User never stuck

**Test Cases:**
```
TC-9.1: Task not found
Input: "Delete cooking task"
Expected: Clear message + "Would you like to see all tasks?"

TC-9.2: Invalid date
Input: "Set due date to yesterday"
Expected: "Dates should be in the future. Did you mean today?"

TC-9.3: Help request
Input: "Help"
Expected: List of capabilities with examples

TC-9.4: Empty input
Input: "" (blank message)
Expected: "What would you like to do?"

TC-9.5: System error
Input: Any (backend down)
Expected: "I'm having trouble right now. Please try again."
```

---

## 🤖 Agent Implementation Plan

**Spec Reference:** `specs/agents/todo-agent.md`

### Agent Configuration

**Component:** OpenAI Agents SDK integration

**Steps:**

1. **Initialize Agent**
   - Model: GPT-4 Turbo
   - Temperature: 0.7 (balanced)
   - Max tokens: 500 (concise responses)
   - Test: Agent initialization

2. **System Prompt**
   - Load: Base system prompt from spec
   - Inject: Current date, user context
   - Include: Tool descriptions
   - Test: Prompt effectiveness

3. **Tool Registration**
   - Register: All 5 MCP tools with schemas
   - Validate: Schema correctness
   - Test: Tool availability

4. **Context Management**
   - Load: Last 20 messages from database
   - Format: OpenAI message format
   - Inject: user_id, session_id
   - Test: Context loading

### Intent Recognition

**Implementation:**

1. **Pattern Matching**
   - CREATE_TODO: "add", "create", "new task", "I need to"
   - LIST_TODOS: "show", "list", "what", "tasks"
   - UPDATE_TODO: "change", "update", "move", "make"
   - COMPLETE_TODO: "finished", "done", "complete", "mark"
   - DELETE_TODO: "delete", "remove", "get rid"
   - SEARCH_TODOS: "find", "search", "look for"
   - Test: Pattern matching accuracy

2. **Function Calling**
   - Use: OpenAI function calling
   - Extract: Parameters from user message
   - Validate: Required parameters present
   - Test: Parameter extraction

3. **Confidence Scoring**
   - High (>0.9): Execute directly
   - Medium (0.7-0.9): Execute with confirmation
   - Low (<0.7): Ask for clarification
   - Test: Confidence thresholds

### Tool Selection Logic

**Decision Tree Implementation:**

```
User Message
    ↓
Intent Recognition (pattern + function calling)
    ↓
    ├─ CREATE_TODO?
    │  └→ Validate: title present? YES → create_todo | NO → ask for title
    │
    ├─ LIST_TODOS?
    │  └→ Extract filters → list_todos with filters
    │
    ├─ UPDATE_TODO?
    │  ├→ Todo identified? NO → search_todos first
    │  ├→ Multiple matches? YES → ask for clarification
    │  └→ YES → update_todo
    │
    ├─ COMPLETE_TODO?
    │  ├→ Todo identified? NO → search_todos first
    │  └→ YES → update_todo(status="completed")
    │
    ├─ DELETE_TODO?
    │  ├→ Todo identified? NO → search_todos first
    │  ├→ Confirmed? NO → ask for confirmation
    │  └→ YES → delete_todo(confirm=true)
    │
    ├─ SEARCH_TODOS?
    │  └→ Query present? YES → search_todos | NO → ask for query
    │
    └─ HELP/GREETING?
       └→ Generate direct response (no tool call)
```

**Test Cases:**
```
TC-A1: Direct tool call
Input: "Add buy milk"
Expected: Immediate create_todo call

TC-A2: Search then action
Input: "Delete the meeting task"
Expected: search_todos → disambiguate → delete_todo

TC-A3: Clarification needed
Input: "Create a task"
Expected: Ask "What should the task be?"

TC-A4: Multi-step flow
Input: "Show tasks" → "Complete the first one"
Expected: list_todos → update_todo (using context)
```

### Response Generation

**Implementation:**

1. **Template Selection**
   - Match: Response type to template
   - Variations: Multiple templates per type
   - Test: Template variety

2. **Formatting**
sp.task   - Emojis: Appropriate use
   - Structure: Bullets/numbers for lists
   - Length: Keep under 150 words
   - Test: Readability

3. **Personalization**
   - Encouragement: For completions
   - Empathy: For errors
   - Proactive: Suggest next actions
   - Test: Tone consistency

### Context and Reference Resolution

**Implementation:**

1. **Task List Storage**
   - Store: Last list_todos result in context
   - Expire: After 5 messages
   - Access: For numeric references
   - Test: Reference accuracy

2. **Last Action Tracking**
   - Track: Last created/updated task
   - Use: For pronoun references ("it", "that")
   - Expire: After 3 messages
   - Test: Pronoun resolution

3. **Search Results Storage**
   - Store: Last search results
   - Use: For disambiguation
   - Expire: After next action
   - Test: Result usage

**Test Cases:**
```
TC-A5: Numeric reference
Input: "Show tasks" (stores list) → "Complete 2"
Expected: Second task from stored list

TC-A6: Pronoun reference
Input: "Add buy milk" (stores task) → "Make it high"
Expected: Just-created task updated

TC-A7: Context expiry
Input: "Show tasks" → [6 messages] → "Complete 1"
Expected: "Which task do you mean?"
```

---

## 🔧 MCP Tools Implementation Plan

**Spec Reference:** `specs/api/mcp-tools.md`

### MCP Server Setup

**Steps:**

1. **Install Official MCP SDK**
   ```bash
   pip install mcp-sdk
   ```

2. **Create MCP Server**
   - File: `mcp_server/server.py`
   - Initialize: Server instance
   - Register: 5 tools
   - Test: Server starts successfully

3. **Configure Connection**
   - Protocol: stdio (standard input/output)
   - Alternative: HTTP (if needed)
   - Test: Agent can connect to server

4. **Environment Variables**
   - PHASE2_API_URL: Phase 2 backend URL
   - INTERNAL_SERVICE_TOKEN: Service-to-service auth
   - Test: Configuration loaded

### Tool 1: create_todo

**Implementation Steps:**

1. **Define Tool Schema**
   ```python
   @mcp_server.tool()
   async def create_todo(
       user_id: int,
       title: str,
       description: Optional[str] = None,
       priority: Optional[str] = "medium",
       due_date: Optional[str] = None
   ) -> dict:
   ```

2. **Input Validation**
   - Validate: user_id > 0
   - Validate: title non-empty, max 200 chars
   - Validate: priority in ["low", "medium", "high"]
   - Validate: due_date is ISO 8601
   - Test: All validation rules

3. **Phase 2 Backend Call**
   - HTTP: POST /todos
   - Headers: Authorization with service token
   - Body: {user_id, title, description, priority, due_date, status="pending"}
   - Test: Backend receives correct data

4. **Response Handling**
   - Success: Return {success: true, todo: {...}}
   - Error: Return {success: false, error: "...", code: "..."}
   - Test: Both paths

5. **Error Handling**
   - Backend unavailable: SERVICE_UNAVAILABLE
   - Validation failed: VALIDATION_ERROR
   - Timeout: TIMEOUT
   - Test: All error types

**Test Cases:**
```
TC-T1.1: Valid create
Input: create_todo(123, "Buy milk")
Expected: {success: true, todo: {id: X, title: "Buy milk"}}

TC-T1.2: Empty title
Input: create_todo(123, "")
Expected: {success: false, code: "VALIDATION_ERROR"}

TC-T1.3: With all fields
Input: create_todo(123, "Task", desc="...", priority="high", due="2025-12-25")
Expected: Todo created with all fields

TC-T1.4: Backend error
Input: create_todo(123, "Task") [backend down]
Expected: {success: false, code: "BACKEND_ERROR"}
```

### Tool 2: list_todos

**Implementation Steps:**

1. **Define Tool Schema**
   ```python
   @mcp_server.tool()
   async def list_todos(
       user_id: int,
       status: Optional[str] = "pending",
       priority: Optional[str] = None,
       due_date: Optional[str] = None,
       due_date_range: Optional[str] = None,
       limit: int = 50,
       offset: int = 0
   ) -> dict:
   ```

2. **Filter Processing**
   - Convert: due_date_range to actual dates
   - Validate: status in ["pending", "completed", "all"]
   - Validate: priority in ["low", "medium", "high"] or None
   - Test: Filter conversion

3. **Phase 2 Backend Call**
   - HTTP: GET /todos?user_id=X&filters...
   - Query params: All filters as query string
   - Test: Correct URL construction

4. **Response Handling**
   - Success: Return {success: true, todos: [...], count: N}
   - Empty: Return {success: true, todos: [], count: 0}
   - Error: Return {success: false, ...}
   - Test: All response types

**Test Cases:**
```
TC-T2.1: List all pending
Input: list_todos(123)
Expected: All pending todos for user 123

TC-T2.2: Filter by priority
Input: list_todos(123, priority="high")
Expected: Only high priority todos

TC-T2.3: Filter by date range
Input: list_todos(123, due_date_range="today")
Expected: Todos due today

TC-T2.4: Empty result
Input: list_todos(123, status="completed") [no completed]
Expected: {success: true, todos: [], count: 0}

TC-T2.5: Pagination
Input: list_todos(123, limit=10, offset=0)
Expected: First 10 todos
```

### Tool 3: update_todo

**Implementation Steps:**

1. **Define Tool Schema**
   ```python
   @mcp_server.tool()
   async def update_todo(
       user_id: int,
       todo_id: int,
       title: Optional[str] = None,
       description: Optional[str] = None,
       status: Optional[str] = None,
       priority: Optional[str] = None,
       due_date: Optional[str] = None
   ) -> dict:
   ```

2. **Input Validation**
   - Validate: At least one field to update
   - Validate: title not empty if provided
   - Validate: status/priority valid enums
   - Test: Validation rules

3. **Build Update Payload**
   - Include: Only provided fields
   - Track: Which fields changed
   - Test: Partial updates

4. **Phase 2 Backend Call**
   - HTTP: PUT /todos/{todo_id}
   - Body: {user_id, ...fields}
   - Test: Correct updates

5. **Response Handling**
   - Success: Return updated todo + changes list
   - Not found: Return NOT_FOUND error
   - Error: Return error details
   - Test: All cases

**Test Cases:**
```
TC-T3.1: Update single field
Input: update_todo(123, 456, priority="high")
Expected: Only priority updated

TC-T3.2: Update multiple fields
Input: update_todo(123, 456, title="New", priority="high")
Expected: Both fields updated

TC-T3.3: Todo not found
Input: update_todo(123, 99999, title="X")
Expected: {success: false, code: "NOT_FOUND"}

TC-T3.4: No fields provided
Input: update_todo(123, 456)
Expected: {success: false, code: "VALIDATION_ERROR"}

TC-T3.5: Complete task
Input: update_todo(123, 456, status="completed")
Expected: Status changed, updated_at timestamp updated
```

### Tool 4: delete_todo

**Implementation Steps:**

1. **Define Tool Schema**
   ```python
   @mcp_server.tool()
   async def delete_todo(
       user_id: int,
       todo_id: int,
       confirm: bool = False
   ) -> dict:
   ```

2. **Confirmation Check**
   - Require: confirm=True explicitly
   - If False: Return CONFIRMATION_REQUIRED
   - Test: Confirmation enforcement

3. **Fetch Todo First**
   - HTTP: GET /todos/{todo_id}?user_id=X
   - Purpose: Get todo details for response
   - Test: Todo retrieval

4. **Delete Todo**
   - HTTP: DELETE /todos/{todo_id}?user_id=X
   - Test: Database deletion

5. **Response Handling**
   - Success: Return deleted todo details
   - Not found: Return NOT_FOUND
   - Not confirmed: Return CONFIRMATION_REQUIRED
   - Test: All paths

**Test Cases:**
```
TC-T4.1: Delete without confirmation
Input: delete_todo(123, 456, confirm=False)
Expected: {success: false, code: "CONFIRMATION_REQUIRED"}

TC-T4.2: Delete with confirmation
Input: delete_todo(123, 456, confirm=True)
Expected: {success: true, deleted_todo: {...}}

TC-T4.3: Todo not found
Input: delete_todo(123, 99999, confirm=True)
Expected: {success: false, code: "NOT_FOUND"}

TC-T4.4: Wrong user
Input: delete_todo(999, 456, confirm=True)
Expected: {success: false, code: "NOT_FOUND"} (access denied)
```

### Tool 5: search_todos

**Implementation Steps:**

1. **Define Tool Schema**
   ```python
   @mcp_server.tool()
   async def search_todos(
       user_id: int,
       query: str,
       status: Optional[str] = "all",
       limit: int = 20
   ) -> dict:
   ```

2. **Query Validation**
   - Validate: Non-empty query
   - Sanitize: Escape special characters
   - Limit: Max 100 characters
   - Test: Query validation

3. **Phase 2 Backend Call**
   - HTTP: GET /todos/search?q=X&user_id=Y
   - Query: Full-text search
   - Test: Search execution

4. **Response Handling**
   - Success: Return matching todos with scores
   - No matches: Return empty array
   - Error: Return error details
   - Test: All cases

**Test Cases:**
```
TC-T5.1: Simple search
Input: search_todos(123, "groceries")
Expected: Todos containing "groceries"

TC-T5.2: Empty query
Input: search_todos(123, "")
Expected: {success: false, code: "VALIDATION_ERROR"}

TC-T5.3: No results
Input: search_todos(123, "xyzabc")
Expected: {success: true, todos: [], count: 0}

TC-T5.4: Search with filter
Input: search_todos(123, "work", status="pending")
Expected: Pending todos containing "work"
```

### Service Authentication

**Implementation:**

1. **Service Token Configuration**
   - Environment: INTERNAL_SERVICE_TOKEN
   - Generate: Secure random token
   - Store: In backend whitelist
   - Test: Token validation

2. **Add to All Requests**
   ```python
   headers = {
       "Authorization": f"Bearer {SERVICE_TOKEN}",
       "X-Internal-Service": "mcp-server"
   }
   ```

3. **Backend Validation**
   - Verify: Token matches expected value
   - Check: X-Internal-Service header
   - Test: Both valid and invalid tokens

---

## 💾 Database Implementation Plan

**Spec Reference:** `specs/database/chat-history.md`

### Schema Creation

**Steps:**

1. **Create Migration File**
   - Tool: Alembic
   - File: `migrations/versions/003_create_chat_history.py`
   - Test: Migration syntax

2. **Define Table**
   ```sql
   CREATE TABLE chat_history (
       id SERIAL PRIMARY KEY,
       user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
       session_id VARCHAR(100) NOT NULL,
       role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
       content TEXT NOT NULL,
       metadata JSONB,
       timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
       is_deleted BOOLEAN NOT NULL DEFAULT FALSE
   );
   ```

3. **Create Indexes**
   ```sql
   CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
   CREATE INDEX idx_chat_history_session_id ON chat_history(session_id);
   CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
   CREATE INDEX idx_chat_history_lookup ON chat_history(user_id, session_id, is_deleted, timestamp DESC);
   ```

4. **Run Migration**
   ```bash
   alembic upgrade head
   ```
   - Test: Table created successfully

### SQLModel Model

**Implementation:**

1. **Define Model**
   ```python
   class ChatHistory(SQLModel, table=True):
       __tablename__ = "chat_history"

       id: Optional[int] = Field(default=None, primary_key=True)
       user_id: int = Field(foreign_key="users.id", index=True)
       session_id: str = Field(index=True, max_length=100)
       role: str = Field(max_length=20)
       content: str
       metadata: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
       timestamp: datetime = Field(default_factory=datetime.utcnow)
       is_deleted: bool = Field(default=False)
   ```

2. **Add Validation**
   - Validate: role in ["user", "assistant", "system"]
   - Validate: content non-empty
   - Test: Model validation

### Query Functions

**Implementation:**

1. **Load Chat History**
   ```python
   async def load_chat_history(
       session: AsyncSession,
       user_id: int,
       session_id: str,
       limit: int = 20
   ) -> list[ChatHistory]:
       statement = (
           select(ChatHistory)
           .where(
               ChatHistory.user_id == user_id,
               ChatHistory.session_id == session_id,
               ChatHistory.is_deleted == False
           )
           .order_by(ChatHistory.timestamp.desc())
           .limit(limit)
       )
       result = await session.execute(statement)
       messages = result.scalars().all()
       return list(reversed(messages))  # Chronological order
   ```
   - Test: Loads last N messages correctly

2. **Save Message**
   ```python
   async def save_message(
       session: AsyncSession,
       user_id: int,
       session_id: str,
       role: str,
       content: str,
       metadata: Optional[Dict] = None
   ) -> ChatHistory:
       message = ChatHistory(
           user_id=user_id,
           session_id=session_id,
           role=role,
           content=content,
           metadata=metadata
       )
       session.add(message)
       await session.commit()
       await session.refresh(message)
       return message
   ```
   - Test: Message saved successfully

3. **Get User Sessions**
   ```python
   async def get_user_sessions(
       session: AsyncSession,
       user_id: int,
       limit: int = 50
   ) -> list[Dict]:
       # SQL: SELECT DISTINCT session_id, MIN(timestamp), MAX(timestamp), COUNT(*)
       # GROUP BY session_id
       # ORDER BY MAX(timestamp) DESC
   ```
   - Test: Returns session summaries

4. **Delete Session (Soft)**
   ```python
   async def delete_session(
       session: AsyncSession,
       user_id: int,
       session_id: str
   ) -> int:
       statement = (
           update(ChatHistory)
           .where(
               ChatHistory.user_id == user_id,
               ChatHistory.session_id == session_id,
               ChatHistory.is_deleted == False
           )
           .values(is_deleted=True)
       )
       result = await session.execute(statement)
       await session.commit()
       return result.rowcount
   ```
   - Test: Messages marked as deleted

5. **Cleanup Old Sessions**
   ```python
   async def cleanup_old_deleted_sessions(
       session: AsyncSession,
       days: int = 90
   ) -> int:
       cutoff = datetime.utcnow() - timedelta(days=days)
       statement = (
           delete(ChatHistory)
           .where(
               ChatHistory.is_deleted == True,
               ChatHistory.timestamp < cutoff
           )
       )
       result = await session.execute(statement)
       await session.commit()
       return result.rowcount
   ```
   - Test: Old messages deleted

**Test Cases:**
```
TC-D1: Load history
Setup: Insert 25 messages
Input: load_chat_history(user_id=123, session_id="sess_1", limit=20)
Expected: Last 20 messages in chronological order

TC-D2: Save message
Input: save_message(123, "sess_1", "user", "Hello")
Expected: Message inserted with correct timestamp

TC-D3: User isolation
Setup: Messages for users 123 and 456
Input: load_chat_history(123, "sess_1")
Expected: Only user 123's messages

TC-D4: Soft delete
Input: delete_session(123, "sess_1")
Expected: Messages marked deleted, not returned in load_chat_history

TC-D5: Cleanup
Setup: Soft-deleted messages from 100 days ago
Input: cleanup_old_deleted_sessions(days=90)
Expected: Old messages permanently deleted
```

---

## 🎨 UI Implementation Plan

**Spec Reference:** `specs/ui/chatkit-integration.md`

### Frontend Setup

**Steps:**

1. **Create React Project**
   ```bash
   npm create vite@latest todo-chat-ui -- --template react-ts
   cd todo-chat-ui
   npm install
   ```

2. **Install Dependencies**
   ```bash
   npm install @openai/chatkit axios zustand react-router-dom
   ```
   - Test: Dependencies installed

3. **Project Structure**
   ```
   src/
   ├── components/
   │   ├── TodoChatInterface.tsx
   │   └── ChatKitWrapper.tsx
   ├── pages/
   │   └── LoginPage.tsx
   ├── stores/
   │   └── authStore.ts
   ├── api/
   │   └── chatApi.ts
   ├── utils/
   │   └── sessionManager.ts
   ├── styles/
   │   └── TodoChatInterface.css
   └── App.tsx
   ```

### Authentication Store

**Implementation:**

1. **Create Zustand Store**
   ```typescript
   interface AuthState {
     token: string | null;
     user: { id: number; email: string } | null;
     isAuthenticated: boolean;
     login: (token: string, user: User) => void;
     logout: () => void;
   }

   export const useAuthStore = create<AuthState>()(
     persist(
       (set) => ({
         token: null,
         user: null,
         isAuthenticated: false,
         login: (token, user) => set({ token, user, isAuthenticated: true }),
         logout: () => set({ token: null, user: null, isAuthenticated: false }),
       }),
       { name: 'auth-storage' }
     )
   );
   ```
   - Test: Store persistence

### Session Management

**Implementation:**

1. **Generate Session ID**
   ```typescript
   function generateSessionId(): string {
     const timestamp = Date.now();
     const random = Math.random().toString(36).substring(2, 10);
     return `sess_${timestamp}_${random}`;
   }
   ```
   - Test: Unique IDs generated

2. **Get/Create Session**
   ```typescript
   function getSessionId(): string {
     const stored = localStorage.getItem('chat_session_id');
     if (stored) return stored;

     const newId = generateSessionId();
     localStorage.setItem('chat_session_id', newId);
     return newId;
   }
   ```
   - Test: Session persistence

3. **New Session**
   ```typescript
   function startNewSession(): string {
     const newId = generateSessionId();
     localStorage.setItem('chat_session_id', newId);
     return newId;
   }
   ```
   - Test: New session created

### API Client

**Implementation:**

1. **Create Axios Instance**
   ```typescript
   const apiClient = axios.create({
     baseURL: import.meta.env.VITE_API_URL,
     timeout: 30000,
     headers: { 'Content-Type': 'application/json' }
   });
   ```

2. **Add Auth Interceptor**
   ```typescript
   apiClient.interceptors.request.use((config) => {
     const token = useAuthStore.getState().token;
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```
   - Test: Token added to requests

3. **Handle 401 Errors**
   ```typescript
   apiClient.interceptors.response.use(
     (response) => response,
     (error) => {
       if (error.response?.status === 401) {
         useAuthStore.getState().logout();
       }
       return Promise.reject(error);
     }
   );
   ```
   - Test: Auto-logout on 401

4. **Send Chat Message**
   ```typescript
   async function sendChatMessage(
     message: string,
     sessionId: string
   ): Promise<ChatResponse> {
     const response = await apiClient.post('/chat', {
       message,
       session_id: sessionId
     });
     return response.data;
   }
   ```
   - Test: Message sent successfully

### Main Chat Component

**Implementation:**

1. **Component State**
   ```typescript
   const [messages, setMessages] = useState<ChatMessage[]>([]);
   const [isLoading, setIsLoading] = useState(false);
   const [sessionId, setSessionId] = useState('');
   ```

2. **Load History on Mount**
   ```typescript
   useEffect(() => {
     const currentSessionId = getSessionId();
     setSessionId(currentSessionId);

     loadChatHistory(currentSessionId)
       .then(setMessages)
       .catch(console.error);
   }, []);
   ```
   - Test: History loaded on mount

3. **Handle Send Message**
   ```typescript
   const handleSendMessage = async (content: string) => {
     // Add user message to UI
     const userMsg = { role: 'user', content, timestamp: new Date().toISOString() };
     setMessages(prev => [...prev, userMsg]);

     setIsLoading(true);
     try {
       // Send to backend
       const response = await sendChatMessage(content, sessionId);

       // Add assistant response
       const assistantMsg = {
         role: 'assistant',
         content: response.response,
         timestamp: response.timestamp
       };
       setMessages(prev => [...prev, assistantMsg]);
     } catch (error) {
       // Show error message
       const errorMsg = {
         role: 'assistant',
         content: "I'm sorry, I encountered an error. Please try again."
       };
       setMessages(prev => [...prev, errorMsg]);
     } finally {
       setIsLoading(false);
     }
   };
   ```
   - Test: Message flow

4. **New Conversation**
   ```typescript
   const handleNewConversation = () => {
     const newSessionId = startNewSession();
     setSessionId(newSessionId);
     setMessages([]);
   };
   ```
   - Test: Session reset

### ChatKit Integration

**Implementation:**

1. **Render ChatKit**
   ```typescript
   <ChatKit
     messages={messages}
     onSendMessage={handleSendMessage}
     isLoading={isLoading}
     placeholder="Ask me about your todos..."
     welcomeMessage="Hello! I'm your AI todo assistant."
     theme="light"
     showTimestamps={true}
     enableMarkdown={true}
   />
   ```
   - Test: ChatKit renders

2. **Custom Message Formatting**
   ```typescript
   renderMessage={(message) => (
     <div className={`message message-${message.role}`}>
       <div className="message-content">
         {formatMessageContent(message.content)}
       </div>
       {message.timestamp && (
         <div className="message-timestamp">
           {formatTimestamp(message.timestamp)}
         </div>
       )}
     </div>
   )}
   ```
   - Test: Messages formatted correctly

### Login Page

**Implementation:**

1. **Login Form**
   ```typescript
   const handleSubmit = async (e: FormEvent) => {
     e.preventDefault();
     setIsLoading(true);

     try {
       const response = await axios.post(`${API_URL}/auth/login`, {
         email,
         password
       });

       const { access_token, user } = response.data;
       login(access_token, user);
       navigate('/chat');
     } catch (error) {
       // Show error
     } finally {
       setIsLoading(false);
     }
   };
   ```
   - Test: Login successful

### Styling

**Implementation:**

1. **Main Layout**
   ```css
   .todo-chat-container {
     display: flex;
     flex-direction: column;
     height: 100vh;
   }

   .chat-header {
     padding: 1rem 2rem;
     background: #fff;
     border-bottom: 1px solid #e0e0e0;
   }

   .chat-main {
     flex: 1;
     overflow: hidden;
   }
   ```

2. **Message Styles**
   ```css
   .message-user {
     background: #007bff;
     color: #fff;
     align-self: flex-end;
   }

   .message-assistant {
     background: #fff;
     color: #333;
     border: 1px solid #e0e0e0;
   }
   ```

3. **Responsive Design**
   ```css
   @media (max-width: 768px) {
     .message {
       max-width: 90%;
       font-size: 0.875rem;
     }
   }
   ```
   - Test: Mobile responsive

**Test Cases:**
```
TC-U1: Initial load
Action: Open app
Expected: Login page if not authenticated

TC-U2: Login flow
Action: Submit credentials
Expected: Redirect to chat, token stored

TC-U3: Send message
Action: Type and send message
Expected: Message appears, loading indicator, response appears

TC-U4: New session
Action: Click "New Chat"
Expected: Messages cleared, new session ID generated

TC-U5: Page reload
Action: Reload browser
Expected: Session persists, history loaded

TC-U6: Logout
Action: Click logout
Expected: Token cleared, redirect to login
```

---

## 🔗 Integration Points

### Frontend ↔ Backend

**Endpoint:** POST /chat

**Request:**
```typescript
{
  message: string;      // User's message
  session_id: string;   // Session identifier
}

Headers: {
  Authorization: "Bearer <jwt_token>"
}
```

**Response:**
```typescript
{
  response: string;     // Assistant's response
  session_id: string;   // Same session ID
  timestamp: string;    // ISO 8601 timestamp
}
```

**Error Response:**
```typescript
{
  error: string;
  code: string;         // e.g., "UNAUTHORIZED", "INTERNAL_ERROR"
  timestamp: string;
}
```

**Status Codes:**
- 200: Success
- 401: Unauthorized (invalid/expired token)
- 400: Bad request (invalid input)
- 500: Internal server error

### Backend ↔ Agent

**Function Call:**
```python
response = await process_chat_message(
    user_id=user_id,           # From JWT
    session_id=session_id,     # From request
    message=user_message,      # From request
    history=chat_history       # From database
)
```

**Agent Response:**
```python
{
    "content": "Agent's response text",
    "metadata": {
        "tool_calls": [...],
        "intent": "CREATE_TODO",
        "confidence": 0.95
    }
}
```

### Agent ↔ MCP Server

**Tool Call Format:**
```json
{
  "tool": "create_todo",
  "parameters": {
    "user_id": 123,
    "title": "Buy milk",
    "priority": "high"
  }
}
```

**Tool Response:**
```json
{
  "success": true,
  "todo": {
    "id": 456,
    "title": "Buy milk",
    "status": "pending",
    "priority": "high"
  },
  "message": "Todo created successfully"
}
```

### MCP Server ↔ Phase 2 Backend

**HTTP Call:**
```python
# MCP Tool calls Phase 2
response = await http_client.post(
    f"{PHASE2_API_URL}/todos",
    json={
        "user_id": user_id,
        "title": title,
        "priority": priority
    },
    headers={
        "Authorization": f"Bearer {SERVICE_TOKEN}",
        "X-Internal-Service": "mcp-server"
    }
)
```

**Phase 2 Response:**
```json
{
  "id": 456,
  "user_id": 123,
  "title": "Buy milk",
  "description": null,
  "status": "pending",
  "priority": "high",
  "due_date": null,
  "created_at": "2025-12-18T10:30:00Z",
  "updated_at": "2025-12-18T10:30:00Z"
}
```

### Backend ↔ Database

**Chat History Save:**
```python
# Save user message
await save_message(
    session=db_session,
    user_id=user_id,
    session_id=session_id,
    role="user",
    content=user_message,
    metadata={"client_ip": request.client.host}
)

# Save assistant response
await save_message(
    session=db_session,
    user_id=user_id,
    session_id=session_id,
    role="assistant",
    content=agent_response["content"],
    metadata=agent_response["metadata"]
)
```

**Chat History Load:**
```python
history = await load_chat_history(
    session=db_session,
    user_id=user_id,
    session_id=session_id,
    limit=20
)

# Format for agent
formatted_history = [
    {"role": msg.role, "content": msg.content}
    for msg in history
]
```

---

## 🧪 Testing Strategy

### Unit Tests

**Backend Tests:**
```python
# Test chat endpoint
async def test_chat_endpoint_success():
    response = await client.post(
        "/chat",
        json={"message": "Add buy milk", "session_id": "sess_test"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

# Test JWT validation
async def test_chat_endpoint_unauthorized():
    response = await client.post("/chat", json={...})
    assert response.status_code == 401
```

**MCP Tools Tests:**
```python
# Test create_todo
async def test_create_todo_success():
    result = await create_todo(123, "Test task")
    assert result["success"] == True
    assert result["todo"]["title"] == "Test task"

# Test validation
async def test_create_todo_empty_title():
    result = await create_todo(123, "")
    assert result["success"] == False
    assert result["code"] == "VALIDATION_ERROR"
```

**Database Tests:**
```python
# Test save message
async def test_save_message():
    msg = await save_message(
        session, 123, "sess_1", "user", "Hello"
    )
    assert msg.id is not None
    assert msg.content == "Hello"

# Test load history
async def test_load_history():
    messages = await load_chat_history(session, 123, "sess_1")
    assert len(messages) > 0
    assert messages[0].role in ["user", "assistant"]
```

**Frontend Tests:**
```typescript
// Test message sending
test('sends message and displays response', async () => {
  render(<TodoChatInterface />);

  const input = screen.getByPlaceholderText('Ask me about your todos...');
  const sendButton = screen.getByRole('button', { name: /send/i });

  fireEvent.change(input, { target: { value: 'Add buy milk' } });
  fireEvent.click(sendButton);

  await waitFor(() => {
    expect(screen.getByText('Add buy milk')).toBeInTheDocument();
  });
});
```

### Integration Tests

**End-to-End Flow:**
```python
async def test_create_todo_flow():
    # 1. User sends message
    response = await client.post(
        "/chat",
        json={"message": "Add buy milk", "session_id": "sess_test"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # 2. Verify response
    assert "created" in response.json()["response"].lower()

    # 3. Verify in database
    todos = await list_todos_from_db(user_id)
    assert any(t.title == "Buy milk" for t in todos)

    # 4. Verify chat history
    history = await load_chat_history(db, user_id, "sess_test")
    assert len(history) == 2  # user + assistant
```

**Multi-Step Conversation:**
```python
async def test_conversation_flow():
    session_id = "sess_test"

    # Step 1: List tasks
    r1 = await send_message("Show my tasks", session_id)
    assert "tasks" in r1["response"].lower()

    # Step 2: Complete first task (using context)
    r2 = await send_message("Complete the first one", session_id)
    assert "completed" in r2["response"].lower()

    # Step 3: Verify in database
    todos = await list_todos_from_db(user_id)
    assert todos[0].status == "completed"
```

### Performance Tests

**Response Time:**
```python
async def test_chat_response_time():
    start = time.time()
    response = await client.post("/chat", json={...})
    elapsed = time.time() - start

    assert elapsed < 2.0  # Must respond within 2 seconds
```

**Concurrent Requests:**
```python
async def test_concurrent_users():
    tasks = [
        send_message("Add task", f"sess_user_{i}")
        for i in range(10)
    ]

    responses = await asyncio.gather(*tasks)

    assert all(r.status_code == 200 for r in responses)
```

### Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Backend API | >90% |
| MCP Tools | >95% |
| Database Queries | >90% |
| Agent Logic | >85% |
| Frontend Components | >80% |

---

## 🚀 Deployment Plan

### Environment Setup

**Development:**
```bash
# Backend
PHASE2_API_URL=http://localhost:8000
DATABASE_URL=postgresql://localhost/todos_dev
INTERNAL_SERVICE_TOKEN=dev_token_123
BETTER_AUTH_SECRET=dev_secret

# Frontend
VITE_API_URL=http://localhost:8001
```

**Production:**
```bash
# Backend
PHASE2_API_URL=https://api.production.com
DATABASE_URL=postgresql://neon.tech/todos_prod
INTERNAL_SERVICE_TOKEN=<secure_token>
BETTER_AUTH_SECRET=<secure_secret>
OPENAI_API_KEY=<api_key>

# Frontend
VITE_API_URL=https://chat-api.production.com
```

### Database Migration

**Steps:**
1. Run migration: `alembic upgrade head`
2. Verify tables created
3. Create indexes
4. Test queries

### Backend Deployment

**Steps:**
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Start MCP server: `python mcp_server/server.py`
4. Start FastAPI: `uvicorn app.main:app --host 0.0.0.0 --port 8001`
5. Health check: `curl http://localhost:8001/health`

### Frontend Deployment

**Steps:**
1. Build: `npm run build`
2. Set env variables
3. Deploy to Vercel/Netlify
4. Configure custom domain
5. Test production build

### Monitoring

**Metrics to Track:**
- Response times (p50, p95, p99)
- Error rates
- Active users
- Messages per session
- Tool call success rates
- Database query performance

**Alerts:**
- Response time > 3s
- Error rate > 5%
- Database connection issues
- MCP server down

---

## ✅ Implementation Checklist

### Phase 1: Foundation
- [ ] Database migration (chat_history table)
- [ ] SQLModel models
- [ ] Database query functions
- [ ] Unit tests for database operations

### Phase 2: MCP Server
- [ ] MCP server setup
- [ ] Implement create_todo tool
- [ ] Implement list_todos tool
- [ ] Implement update_todo tool
- [ ] Implement delete_todo tool
- [ ] Implement search_todos tool
- [ ] Service authentication
- [ ] Unit tests for all tools
- [ ] Integration tests with Phase 2

### Phase 3: AI Agent
- [ ] OpenAI Agent configuration
- [ ] System prompt implementation
- [ ] Intent recognition logic
- [ ] Tool selection logic
- [ ] Response generation
- [ ] Context management
- [ ] Reference resolution
- [ ] Unit tests for agent

### Phase 4: Backend API
- [ ] Chat endpoint implementation
- [ ] JWT validation middleware
- [ ] History loading
- [ ] Message saving
- [ ] Error handling
- [ ] Unit tests
- [ ] Integration tests

### Phase 5: Frontend
- [ ] React project setup
- [ ] Authentication store
- [ ] Session management
- [ ] API client
- [ ] Login page
- [ ] Main chat interface
- [ ] ChatKit integration
- [ ] Styling
- [ ] Component tests

### Phase 6: Testing
- [ ] Unit tests (>90% coverage)
- [ ] Integration tests
- [ ] E2E conversation flows
- [ ] Performance tests
- [ ] Security tests
- [ ] User acceptance testing

### Phase 7: Deployment
- [ ] Environment configuration
- [ ] Database migration (production)
- [ ] Backend deployment
- [ ] Frontend deployment
- [ ] Monitoring setup
- [ ] Load testing
- [ ] Documentation

---

## 📊 Success Criteria

**Functional:**
- ✅ All 9 features working as specified
- ✅ Agent correctly interprets >90% of requests
- ✅ MCP tools successfully execute all operations
- ✅ Chat history persists across sessions
- ✅ Authentication works seamlessly

**Non-Functional:**
- ✅ Response time <2s for typical requests
- ✅ >95% uptime
- ✅ Handles 100 concurrent users
- ✅ >90% test coverage
- ✅ No data leakage between users

**User Experience:**
- ✅ Natural conversation flow
- ✅ Clear, helpful responses
- ✅ Graceful error handling
- ✅ Mobile responsive
- ✅ Fast and reliable

---

**Status:** Plan complete and ready for task breakdown
**Next Step:** Break down into testable tasks for implementation via Claude Code
**Last Updated:** 2025-12-18
