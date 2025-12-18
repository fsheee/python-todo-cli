# Phase 3: AI-Powered Chatbot Todo Manager - Overview

## 🎯 Objective

Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture, Claude Code, and Spec-Kit Plus.

## 💡 Development Approach

Use the Agentic Dev Stack workflow:
1. **Write spec** → Define all requirements and architecture
2. **Generate plan** → Break down into implementation phases
3. **Break into tasks** → Create testable, atomic tasks
4. **Implement via Claude Code** → No manual coding allowed

**Rule:** All development must be spec-driven. We will review the process, prompts, and iterations to judge each phase and project.

---

## 📋 Core Requirements

### Conversational Interface
- Implement conversational interface for all Basic Level todo features
- Natural language processing for task operations (create, read, update, delete)
- Context-aware responses that understand user intent
- Graceful handling of ambiguous requests

### AI Framework
- Use **OpenAI Agents SDK** for AI logic and decision-making
- Agent interprets user intent and determines appropriate actions
- Stateless agent design with context loaded from database

### MCP Server Architecture
- Build MCP server with **Official MCP SDK**
- Expose all task operations as MCP tools
- Tools are stateless and store state in database
- AI agents use MCP tools to manage tasks

### Stateless Design
- Stateless chat endpoint that persists conversation state to database
- No in-memory session storage
- All context retrieved from database per request
- Scalable and horizontally distributable

### Phase 2 Integration
- Reuse existing Phase 2 CRUD logic
- Reuse Better Auth authentication system
- Do not rewrite existing business logic
- MCP tools wrap Phase 2 backend endpoints

---

## 🛠 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | OpenAI ChatKit | Chat UI component |
| **Backend** | Python FastAPI | REST API server |
| **AI Framework** | OpenAI Agents SDK | Natural language understanding & intent detection |
| **MCP Server** | Official MCP SDK | Tool execution layer |
| **ORM** | SQLModel | Database models and queries |
| **Database** | Neon Serverless PostgreSQL | Data persistence |
| **Authentication** | Better Auth | User authentication (reused from Phase 2) |

---

## 🏗 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                     OpenAI ChatKit (React)                   │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP/WebSocket
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                     │
│  ┌────────────────────┐         ┌─────────────────────┐    │
│  │  Better Auth       │         │  Chat Endpoint      │    │
│  │  (Phase 2 Reused)  │────────▶│  /chat (POST)       │    │
│  │  - JWT Validation  │         │  - Load History     │    │
│  │  - User Context    │         │  - Call AI Agent    │    │
│  └────────────────────┘         │  - Save Response    │    │
│                                  └──────────┬──────────┘    │
└─────────────────────────────────────────────┼───────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │    OpenAI Agents SDK              │
                            │  - Intent Recognition             │
                            │  - Context Understanding          │
                            │  - Tool Selection & Invocation    │
                            └─────────────────┬─────────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │         MCP Server                │
                            │      (Official MCP SDK)           │
                            │  ┌─────────────────────────────┐ │
                            │  │ MCP Tools (Stateless)       │ │
                            │  │ - create_todo               │ │
                            │  │ - list_todos                │ │
                            │  │ - update_todo               │ │
                            │  │ - delete_todo               │ │
                            │  │ - search_todos              │ │
                            │  └──────────────┬──────────────┘ │
                            └─────────────────┼─────────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │    Phase 2 Backend Logic          │
                            │    (CRUD Operations - Reused)     │
                            └─────────────────┬─────────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │    SQLModel ORM Layer             │
                            └─────────────────┬─────────────────┘
                                              │
                            ┌─────────────────▼─────────────────┐
                            │  Neon Serverless PostgreSQL       │
                            │  - todos table                    │
                            │  - users table                    │
                            │  - chat_history table             │
                            └───────────────────────────────────┘
```

---

## 🔄 Request Flow

1. **User sends message** via ChatKit UI
2. **Frontend** → POST `/chat` with message and session_id
3. **Backend validates JWT** → Extract user_id from token
4. **Load chat history** → Retrieve from database by session_id and user_id
5. **Initialize AI Agent** → OpenAI Agents SDK with conversation context
6. **Agent processes** → Understands intent, determines action
7. **Agent calls MCP tool** → Appropriate tool based on intent
8. **MCP tool executes** → Calls Phase 2 backend CRUD operations
9. **Phase 2 backend** → Performs database operation via SQLModel
10. **Response bubbles up** → MCP tool → Agent → Backend
11. **Save to history** → Store user message + assistant response
12. **Return to frontend** → JSON response with AI message
13. **ChatKit displays** → Show response in chat UI

---

## 📊 Core Data Models

### Todo (Phase 2 - Reused)
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, completed
    priority: Optional[str] = None  # low, medium, high
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### User (Phase 2 - Reused)
```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### ChatHistory (Phase 3 - New)
```python
class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    session_id: str = Field(index=True)
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict] = Field(default=None)  # Store tool calls, etc.
```

---

## 🔌 MCP Tools Overview

All tools are defined in `/specs/api/mcp-tools.md`. Summary:

| Tool | Purpose | Phase 2 Endpoint Used |
|------|---------|---------------------|
| `create_todo` | Create new todo | POST /todos |
| `list_todos` | Get user's todos with filters | GET /todos |
| `update_todo` | Modify existing todo | PUT /todos/{id} |
| `delete_todo` | Delete a todo | DELETE /todos/{id} |
| `search_todos` | Search todos by keyword | GET /todos?search={query} |

**Key Principles:**
- Tools are stateless
- Tools receive verified `user_id` from backend
- Tools never handle authentication
- Tools wrap existing Phase 2 logic

---

## 🔐 Authentication Flow (Phase 2 Reused)

1. User registers/logs in via Better Auth
2. Backend issues JWT token with user_id
3. Frontend stores token
4. All API requests include `Authorization: Bearer <token>` header
5. FastAPI middleware validates token using `BETTER_AUTH_SECRET`
6. Extract user_id from validated token
7. Pass user_id to AI agent context
8. Agent passes user_id to MCP tools
9. MCP tools use user_id for all database operations

**Important:** Phase 3 does NOT implement authentication. It only uses the existing Better Auth system from Phase 2.

---

## 🎨 User Experience Examples

### Creating a Todo
```
User: "I need to buy groceries tomorrow"
AI: "I've created a new todo: 'Buy groceries' with due date set to tomorrow.
     Would you like to set a priority level?"
```

### Listing Todos
```
User: "What do I need to do today?"
AI: "You have 3 tasks for today:
     1. Buy groceries (due today, high priority)
     2. Call dentist (due today)
     3. Review meeting notes (due today, low priority)

     Would you like details on any of these?"
```

### Completing a Todo
```
User: "I finished the groceries"
AI: "Great work! I've marked 'Buy groceries' as completed.
     You have 2 tasks remaining for today."
```

### Updating a Todo
```
User: "Move the dentist appointment to next Monday"
AI: "I've updated 'Call dentist' with a due date of next Monday (Dec 23).
     Would you like me to set a reminder?"
```

---

## 📁 Specification Structure

This overview references detailed specs:

```
specs/
├── overview.md                    ← You are here
├── features/
│   └── chatbot.md                ← Conversational interface spec
├── agents/
│   └── todo-agent.md             ← AI agent behavior & prompts
├── api/
│   └── mcp-tools.md              ← MCP tool definitions
├── database/
│   └── chat-history.md           ← Chat history schema & persistence
└── ui/
    └── chatkit-integration.md    ← Frontend integration
```

---

## ✅ Success Criteria

1. Users can manage todos entirely through natural language
2. AI correctly interprets user intent (>90% accuracy)
3. MCP server successfully exposes all CRUD operations
4. Chat endpoint is stateless with database-persisted history
5. Authentication works seamlessly (Better Auth reused)
6. All operations correctly attributed to authenticated user
7. System handles errors gracefully with helpful messages
8. Conversation context maintained across sessions
9. Response time < 2 seconds for typical requests
10. Entire implementation via Claude Code workflow (no manual coding)

---

## 🚀 Implementation Phases

### Phase 1: Database & Models
- Extend database schema with ChatHistory table
- Create SQLModel models for chat persistence
- Test database migrations

### Phase 2: MCP Server Setup
- Install and configure Official MCP SDK
- Implement 5 core tools (create, list, update, delete, search)
- Test tools independently with mock data
- Ensure stateless design

### Phase 3: AI Agent Configuration
- Set up OpenAI Agents SDK
- Configure agent with MCP tools
- Define system prompts and behavior
- Test intent recognition

### Phase 4: Backend API Integration
- Create `/chat` endpoint in FastAPI
- Connect OpenAI Agent to MCP server
- Implement chat history persistence
- Add error handling and logging

### Phase 5: Frontend Development
- Set up OpenAI ChatKit component
- Connect to backend `/chat` endpoint
- Handle authentication flow
- Display conversation history

### Phase 6: Testing & Refinement
- End-to-end conversation testing
- Edge case handling
- Performance optimization
- User feedback iteration

---

## 📝 Development Rules (Per Constitution)

1. **Spec-First:** All features defined in specs before implementation
2. **No Manual Coding:** Claude Code generates all implementation
3. **Reference Specs:** All code changes must reference their spec
4. **Stateless Design:** No in-memory state, all persistence in database
5. **Reuse Phase 2:** Never rewrite existing CRUD or auth logic
6. **MCP Tools Only:** Only MCP tools access database operations
7. **Verified Identity:** user_id always from validated JWT, never from input

---

## 🔗 Related Documents

- [CLAUDE.md](../CLAUDE.md) - Full project constitution
- [AGENTS.md](../AGENTS.md) - Agent definitions and hierarchy
- [.specify/memory/constitution.md](../.specify/memory/constitution.md) - Spec-Kit constitution

---

## 📅 Timeline

Timeline estimation not included per constitution. Focus on delivering complete, working features in phases.

---

## 🎯 Next Steps

1. Review and approve this overview
2. Create detailed feature specs in `/specs/features/`
3. Define agent behavior in `/specs/agents/`
4. Specify MCP tools in `/specs/api/`
5. Generate implementation plan
6. Break plan into testable tasks
7. Execute via Claude Code

---

**Last Updated:** 2025-12-18
**Status:** Draft - Awaiting Approval
