# Hackathon Todo - Multi-Phase Full-Stack Application

A comprehensive todo management system evolved through three phases: from a simple CLI app to a full-stack web application with AI-powered conversational interface.

## 🏆 Project Overview

This project demonstrates spec-driven development using Claude Code and Spec-Kit Plus, implementing a complete todo management system across three distinct phases.

### Phase 1: Console Application
A command-line todo application with in-memory storage, featuring basic CRUD operations.

### Phase 2: Web Application
A secure, modern, multi-user web application with authentication, RESTful API, and responsive UI.

### Phase 3: AI Chatbot
An AI-powered conversational interface for natural language todo management using OpenAI Agents SDK and MCP tools.

---

## 📁 Project Structure

```
hackathon-todo/
├── phase1-console/          # CLI todo application (Python)
│   ├── src/                 # Source code
│   ├── tests/               # Unit tests
│   └── specs/               # Feature specifications
│
├── phase2-web/              # Web application
│   ├── backend/             # FastAPI backend
│   │   ├── routes/          # API endpoints
│   │   ├── models.py        # Database models
│   │   └── auth.py          # Authentication logic
│   ├── frontend/            # Next.js frontend
│   │   ├── src/app/         # App router pages
│   │   ├── src/components/  # React components
│   │   └── src/lib/         # Utilities and API client
│   └── specs/               # API and feature specs
│
├── phase3-chatbot/          # AI chatbot interface
│   ├── app/                 # FastAPI backend
│   │   ├── agents/          # AI agent implementation
│   │   ├── routes/          # Chat and history endpoints
│   │   └── middleware/      # Auth and rate limiting
│   ├── mcp_server/          # MCP tool server
│   │   └── tools/           # Todo operation tools
│   ├── frontend/            # Next.js chat interface
│   └── specs/               # Agent and tool specs
│
└── .claude/                 # Shared skills and agents
    └── skills/              # Reusable skill definitions
```

---

## 🚀 Quick Start

### Phase 1: Console App

```bash
cd phase1-console
uv run python src/main.py
```

### Phase 2: Web Application

**Backend:**
```bash
cd phase2-web/backend
uv venv
uv add fastapi sqlmodel psycopg2-binary python-dotenv
uvicorn main:app --reload
```

**Frontend:**
```bash
cd phase2-web/frontend
npm install
npm run dev
```

### Phase 3: Chatbot

**Backend:**
```bash
cd phase3-chatbot
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd phase3-chatbot/frontend
npm install
npm run dev
```

---

## 💻 Technology Stack

### Phase 1 (Console)
- **Language:** Python 3.13+
- **Storage:** In-memory
- **Testing:** pytest

### Phase 2 (Web)
- **Backend:** Python 3.13+, FastAPI, SQLModel
- **Database:** Neon PostgreSQL (serverless)
- **Authentication:** Better Auth with JWT
- **Frontend:** Next.js 15+, TypeScript, Tailwind CSS
- **Deployment:** Vercel (frontend + backend serverless)

### Phase 3 (Chatbot)
- **AI Framework:** OpenAI Agents SDK
- **MCP Server:** Official MCP SDK
- **Tools:** 5 MCP tools (create, list, update, delete, search)
- **Chat UI:** OpenAI ChatKit + Next.js
- **Backend:** FastAPI with rate limiting
- **Storage:** File-based chat history + PostgreSQL

---

## ✨ Key Features

### Phase 1 Features
- ✅ View all tasks with status indicators
- ✅ Add new tasks with title and description
- ✅ Update task details
- ✅ Delete tasks
- ✅ Toggle complete/incomplete status

### Phase 2 Features
- 🔐 User authentication (signup, signin, password reset)
- ✅ Full CRUD operations for todos
- 🎯 Priority levels (low, medium, high)
- 📅 Due dates with calendar picker
- 🎨 Modern glass morphism UI design
- 📱 Responsive mobile-friendly interface
- 🔒 JWT-based authorization
- 🗄️ PostgreSQL database persistence
- 🚀 Production deployment on Vercel

### Phase 3 Features
- 🤖 Natural language todo management
- 💬 Conversational AI interface
- 🎯 Intent recognition and context awareness
- 🔧 5 MCP tools for todo operations
- 📊 Chat history persistence
- 🔄 Session continuity
- ⚡ Real-time responses
- 🛡️ Rate limiting and security

---

## 🔐 Authentication

All phases integrate with **Better Auth**:
- User registration and login
- JWT token-based authentication
- Secure password hashing with bcrypt
- Session management
- Password reset functionality

**Environment Variables:**
```bash
# Backend (.env)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your_secret_key_here
JWT_SECRET=your_jwt_secret_here
```

---

## 📊 Database Schema

### Users Table
- `id` (primary key)
- `name`
- `email` (unique)
- `password_hash`
- `created_at`
- `updated_at`

### Todos Table
- `id` (primary key)
- `user_id` (foreign key)
- `title`
- `description`
- `status` (pending/completed)
- `priority` (low/medium/high)
- `due_date`
- `created_at`
- `updated_at`

### Chat History Table (Phase 3)
- `id` (primary key)
- `user_id` (foreign key)
- `session_id`
- `role` (user/assistant)
- `content`
- `metadata`
- `timestamp`

---

## 🧪 Testing

### Phase 1
```bash
cd phase1-console
uv run pytest -v
```

**Coverage:** 34 tests covering all CRUD operations

### Phase 2
```bash
cd phase2-web/backend
pytest tests/ -v
```

**Coverage:** Integration tests for auth and CRUD endpoints

### Phase 3
```bash
cd phase3-chatbot
pytest tests/ -v
```

**Coverage:** Unit tests for MCP tools and agent logic

---

## 📖 API Documentation

### Phase 2 REST Endpoints

**Authentication:**
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/refresh` - Refresh JWT token

**Todos:**
- `GET /api/todos` - List all todos (with filters)
- `POST /api/todos` - Create new todo
- `GET /api/todos/{id}` - Get todo by ID
- `PUT /api/todos/{id}` - Update todo
- `DELETE /api/todos/{id}` - Delete todo

### Phase 3 Chat Endpoints

**Chat:**
- `POST /api/chat` - Send message to AI agent
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history/{session_id}` - Clear session

**MCP Tools:**
- `create_todo` - Create new todo
- `list_todos` - List todos with filters
- `update_todo` - Update existing todo
- `delete_todo` - Delete todo (with confirmation)
- `search_todos` - Search by keyword

---

## 🎯 Usage Examples

### Phase 1: CLI
```
$ uv run python src/main.py

Todo Application
1. View all tasks
2. Add new task
3. Update task
4. Delete task
5. Toggle complete/incomplete
6. Exit

Enter your choice: 2
Enter task title: Buy groceries
Enter task description: Milk, eggs, bread
✓ Task added successfully!
```

### Phase 2: Web API
```bash
# Create a todo
curl -X POST https://your-app.vercel.app/api/todos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high", "due_date": "2025-12-25"}'
```

### Phase 3: Chat
```
User: "I need to buy groceries tomorrow"

AI: "I've created a todo for you:
     📝 Buy groceries
     📅 Due: Tomorrow (Dec 19, 2025)

     Would you like to set a priority?"

User: "Make it high priority"

AI: "Updated! 'Buy groceries' is now high priority."
```

---

## 🌐 Deployment

### Phase 2 Deployment

**Backend (Vercel Serverless):**
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main

**Frontend (Vercel):**
1. Configure Next.js project in Vercel
2. Set `NEXT_PUBLIC_API_URL` environment variable
3. Deploy with automatic SSL

**Database (Neon):**
1. Create Neon PostgreSQL database
2. Copy connection string to `DATABASE_URL`
3. Run migrations

### Phase 3 Deployment

**Backend:**
```bash
# Set environment variables
export DATABASE_URL=...
export OPENAI_API_KEY=...
export BETTER_AUTH_SECRET=...

# Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# Set API URL
export NEXT_PUBLIC_API_URL=https://your-backend.com

# Build and deploy
npm run build
npm start
```

---

## 🔧 Development Workflow

This project follows a **spec-driven development** approach:

1. **Define Specs** - Write feature specifications in `/specs/`
2. **Generate Code** - Use Claude Code to implement from specs
3. **Test** - Run automated tests
4. **Review** - Check generated code against specs
5. **Deploy** - Push to production

**Key Principles:**
- ✅ Specifications are the source of truth
- ✅ All features must have specs first
- ✅ No manual code editing without spec updates
- ✅ Claude Code automates implementation

---

## 📚 Documentation

- [Phase 1 README](./phase1-console/README.md)
- [Phase 2 README](./phase2-web/README.md)
- [Phase 3 README](./phase3-chatbot/README.md)
- [Phase 2 Backend Docs](./phase2-web/backend/README.md)
- [Phase 2 Frontend Docs](./phase2-web/frontend/README.md)
- [Architecture Decision Records](./phase2-web/adr/)
- [Shared Skills](./claude/skills/)

---

## 🤝 Contributing

This project is part of a hackathon demonstration. Contributions should follow the spec-driven workflow:

1. Create a feature spec in `/specs/`
2. Use Claude Code to generate implementation
3. Write tests
4. Submit PR with spec reference

---

## 📝 License

MIT License - See individual phase directories for details

---

## 🎓 Learning Resources

This project demonstrates:
- **Spec-Driven Development** with Claude Code
- **RESTful API Design** with FastAPI
- **Modern Frontend** with Next.js and TypeScript
- **AI Agent Development** with OpenAI Agents SDK
- **MCP Tool Creation** for LLM integration
- **Full-Stack Deployment** on Vercel
- **Database Design** with PostgreSQL
- **Authentication** with JWT tokens

---

## 🆘 Support

For issues or questions:
- Check the [phase-specific READMEs](./phase1-console/README.md)
- Review the [specifications](./phase2-web/specs/)
- Open an issue on GitHub

---

**Built with Claude Code** 🤖

*Demonstrating the power of spec-driven development and AI-assisted coding*
