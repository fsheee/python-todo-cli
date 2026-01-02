# Contributing to Phase 3 Chatbot

## 🎯 Welcome Contributors!

Thank you for your interest in contributing to the Phase 3 AI-powered chatbot todo manager!

This project follows **Spec-Driven Development (SDD)** using Claude Code and Spec-Kit Plus.

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Workflow](#development-workflow)
3. [Architecture Overview](#architecture-overview)
4. [Code Standards](#code-standards)
5. [Testing Requirements](#testing-requirements)
6. [Submitting Changes](#submitting-changes)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Node.js 18+
- Git
- PostgreSQL (or Neon account)
- OpenAI API key

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/your-org/hackathon-todo.git
cd hackathon-todo/phase3-chatbot

# Backend setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
cd ..

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run migrations
alembic upgrade head
```

### Run Development Environment

```bash
# Terminal 1: MCP Server
python mcp_server/server.py

# Terminal 2: Backend API
uvicorn app.main:app --reload --port 8001

# Terminal 3: Frontend
cd frontend && npm run dev
```

Visit: `http://localhost:3000`

---

## 🔄 Development Workflow

### Phase 3 follows Spec-Driven Development (SDD)

**Rule:** ALL changes must start with a specification!

### Workflow Steps

1. **Write Specification**
   ```bash
   # Create or update spec in specs/
   nano specs/features/new-feature.md
   ```

2. **Create Implementation Plan**
   ```bash
   # Use Claude Code
   /sp.plan
   ```

3. **Break Down into Tasks**
   ```bash
   /sp.tasks
   ```

4. **Implement Tasks**
   ```bash
   /sp.implement
   ```

5. **Test Implementation**
   ```bash
   pytest tests/ -v
   ```

6. **Document Changes**
   ```bash
   # Update README, CHANGELOG, etc.
   ```

### No Manual Coding!

**❌ DON'T:**
- Edit code files directly
- Add features without specs
- Skip the specification step
- Bypass the workflow

**✅ DO:**
- Write specs first
- Use Claude Code for implementation
- Follow the SDD workflow
- Document all decisions

---

## 🏗️ Architecture Overview

### System Layers

```
Frontend (Next.js + ChatKit)
    ↓
Backend API (FastAPI)
    ↓
AI Agent (OpenAI GPT-4)
    ↓
MCP Server (5 tools)
    ↓
Phase 2 Backend (CRUD)
    ↓
Database (PostgreSQL)
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Frontend** | `frontend/` | Next.js chat UI |
| **Backend API** | `app/` | FastAPI endpoints |
| **AI Agent** | `app/agents/` | OpenAI agent logic |
| **MCP Server** | `mcp_server/` | Tool execution layer |
| **Database** | `app/models/`, `app/queries/` | Data persistence |
| **Tests** | `tests/` | All test files |
| **Specs** | `specs/` | Feature specifications |

### Important Principles

1. **Stateless Design** - All state in database
2. **User Isolation** - Enforced at every layer
3. **Phase 2 Reuse** - Never rewrite business logic
4. **Single Agent** - One AI agent handles all
5. **5 MCP Tools** - Execute all operations
6. **Spec-Driven** - Every line traceable to specs

---

## 📝 Code Standards

### Python (Backend, MCP, Agent)

**Style Guide:** PEP 8

**Type Hints Required:**
```python
# ✅ GOOD
async def save_message(
    session: AsyncSession,
    user_id: int,
    session_id: str,
    role: str,
    content: str,
    metadata: Optional[Dict] = None
) -> ChatHistory:
    """Save a chat message to database."""
    pass

# ❌ BAD
async def save_message(session, user_id, session_id, role, content, metadata=None):
    pass
```

**Async/Await:**
```python
# ✅ GOOD - Use async for I/O operations
async def load_history(session: AsyncSession, user_id: int) -> list:
    result = await session.execute(query)
    return result.scalars().all()

# ❌ BAD - Blocking I/O
def load_history(session, user_id):
    return session.execute(query).scalars().all()
```

**Error Handling:**
```python
# ✅ GOOD - Specific exceptions, user-friendly messages
try:
    result = await mcp_tool.create_todo(user_id, title)
except ValidationError as e:
    return {"error": "Invalid input", "code": "VALIDATION_ERROR"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "Something went wrong", "code": "INTERNAL_ERROR"}

# ❌ BAD - Bare except, technical messages
try:
    result = await mcp_tool.create_todo(user_id, title)
except:
    return {"error": str(e)}  # Exposes internals!
```

### TypeScript (Frontend)

**Style Guide:** Airbnb TypeScript

**Type Definitions:**
```typescript
// ✅ GOOD - Strong types
interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

// ❌ BAD - Any types
interface ChatMessage {
  role: any;
  content: any;
  timestamp: any;
}
```

**React Hooks:**
```typescript
// ✅ GOOD - Proper dependency arrays
useEffect(() => {
  loadHistory(sessionId);
}, [sessionId]);

// ❌ BAD - Missing dependencies
useEffect(() => {
  loadHistory(sessionId);
}, []);
```

### Documentation

**Every function needs a docstring:**

```python
async def load_chat_history(
    session: AsyncSession,
    user_id: int,
    session_id: str,
    limit: int = 20
) -> list[ChatHistory]:
    """
    Load recent chat messages for a user session.

    Args:
        session: Database session
        user_id: ID of the user (from JWT)
        session_id: Session identifier
        limit: Max messages to return (default: 20)

    Returns:
        List of ChatHistory objects in chronological order

    Raises:
        DatabaseError: If query fails
    """
    pass
```

---

## 🧪 Testing Requirements

### Test Coverage Targets

| Component | Coverage | Required |
|-----------|----------|----------|
| Database | >90% | Yes |
| MCP Tools | >95% | Yes |
| Agent | >85% | Yes |
| Backend API | >90% | Yes |
| Frontend | >80% | Optional |

### Writing Tests

**Test File Naming:**
- Unit tests: `tests/unit/test_*.py`
- Integration tests: `tests/integration/test_*.py`
- E2E tests: `tests/e2e/test_*.py`

**Test Class Naming:**
```python
class TestChatHistoryModel:  # Test{ComponentName}
    """Test ChatHistory SQLModel validation."""

    async def test_create_with_all_fields(self):
        """TC-X.Y.Z: Test description"""
        # Arrange
        # Act
        # Assert
```

**Test Case IDs:**
- Format: `TC-X.Y.Z` (from specs/TASKS.md)
- Include in docstring
- Traceable to specifications

**Example Test:**
```python
@pytest.mark.asyncio
async def test_save_message_success(self, db_session, test_user_id):
    """
    TC-1.5.1: Save user message - succeeds, returns ID

    Spec: specs/database/chat-history.md - Query 2
    """
    # Arrange
    session_id = "sess_test"
    content = "Test message"

    # Act
    message = await save_message(
        db_session, test_user_id, session_id, "user", content
    )

    # Assert
    assert message.id is not None
    assert message.content == content
    assert message.user_id == test_user_id
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/integration/test_database.py -v

# With coverage
pytest tests/ --cov=app --cov=mcp_server --cov-report=html

# View coverage
open htmlcov/index.html
```

---

## 🔀 Submitting Changes

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `test/` - Test additions
- `refactor/` - Code refactoring

**Examples:**
- `feature/add-reminder-notifications`
- `fix/chat-history-pagination`
- `docs/update-api-guide`

### Commit Messages

Follow Conventional Commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance

**Examples:**
```
feat(agent): add reminder notification support

Implements reminder notifications for overdue tasks.

Spec: specs/features/reminders.md
Tasks: T101-T105
```

```
fix(mcp): handle backend timeout in list_todos

Previously, timeouts caused 500 errors. Now returns
friendly error message and retries.

Fixes #42
```

### Pull Request Process

1. **Create PR from your branch**
2. **Fill out PR template:**
   - Description of changes
   - Link to specification
   - Task IDs completed
   - Test coverage
   - Screenshots (if UI changes)

3. **Ensure CI passes:**
   - All tests green
   - Coverage meets targets
   - Linting passes

4. **Request review** from maintainers

5. **Address feedback**

6. **Merge** when approved

---

## 🔍 Code Review Guidelines

### For Reviewers

**Check for:**
- ✅ Specification reference included
- ✅ Type hints present
- ✅ Tests included
- ✅ Docstrings added
- ✅ Error handling implemented
- ✅ No security issues
- ✅ Follows code standards

**Questions to Ask:**
- Is this change necessary?
- Does it follow the spec?
- Are there tests?
- Is it the simplest solution?
- Are there any edge cases?

---

## 📚 Resources

### Documentation

- **Specifications:** `specs/` directory
- **Implementation Plan:** `specs/PLAN.md`
- **Task Breakdown:** `specs/TASKS.md`
- **Constitution:** `CLAUDE.md`
- **API Docs:** `API_DOCUMENTATION.md`
- **User Guide:** `USER_GUIDE.md`

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI Agents SDK](https://platform.openai.com/docs/agents)
- [MCP Protocol](https://github.com/modelcontextprotocol/specification)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🤝 Getting Help

### For Contributors

1. **Check existing specs** in `specs/` first
2. **Read CLAUDE.md** for project principles
3. **Ask questions** in GitHub discussions
4. **Join our community** (if applicable)

### For Maintainers

- Review PRs within 48 hours
- Provide constructive feedback
- Help new contributors
- Keep documentation updated

---

## 🎯 Good First Issues

Looking to contribute? Start with these:

- Add more test cases
- Improve error messages
- Expand documentation
- Fix typos
- Add code comments
- Improve type hints

Label: `good-first-issue`

---

## 📜 License

This project is part of the hackathon-todo repository.

See LICENSE file in repository root for details.

---

## 🙏 Thank You!

Your contributions make this project better for everyone!

**Happy coding!** 🚀

---

**Contributing Guide Version:** 1.0.0
**Last Updated:** 2025-12-25
**Project:** Phase 3 AI Chatbot Todo Manager
