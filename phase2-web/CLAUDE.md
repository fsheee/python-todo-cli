# CLAUDE.md — Phase 2 Constitution

## 🏆 Project Overview
This repo implements Phase 2 of the hackathon-todo project: a secure, modern, multi-user web todo app evolved from the original console app.  
Development is **spec-driven** using Spec-Kit Plus and Claude Code—**NO manual implementation code editing is allowed.** All features, APIs, and models must be defined in specs first.

---

## 📚 Spec-Kit Directory Structure

- `/specs/overview.md` — Project/phasing summary
- `/specs/features/` — All feature-level specs (`task-crud.md`, `authentication.md`, etc.)
- `/specs/api/` — REST API endpoint specification (`rest-endpoints.md`)
- `/specs/database/` — Tables and model definitions (`schema.md`)
- `/specs/ui/` — UI specs (components/pages as needed)
- `/specs/agents/` — Agent and subagent specs
- `/specs/agents/skills/` — Reusable agent skill specs
- `.claude/skills/` — **Shared skills for Phase 2/3 reuse**

_Spec-Kit config file: `/phase2/.spec-kit/config.yaml`_

---

## 🚦 Development Workflow & Rules

1. **Start by reading the relevant spec before any code/feature change.**
2. **DO NOT manually edit backend or frontend implementation code.**
   - Only update/add to the appropriate `.md` spec in `/specs/`.
   - Re-run Claude Code or Spec-Kit automation to regenerate/update code from specs.
3. **Reference specs explicitly in Claude Code and Pull Request summaries:**
   - `@specs/features/task-crud.md`
   - `@specs/features/authentication.md`
   - `@specs/api/rest-endpoints.md`
   - `@specs/database/schema.md`
   - `@specs/agents/todo-agent.md`
   - `.claude/skills/SKILLS.md` - **Shared skills index**
   - `.claude/skills/01-core/task/create-task.md`

---

## 🤖 Agents, Subagents, and Skills

- **Agents** are defined in `/specs/agents/` and operate as modular AI components for concatenated workflows (e.g., todo management, user auth).
- **Subagents** specialize in micro-flows for specific features or integrations (e.g., task CRUD, verification).
- **Skills** are reusable behaviors written for both backend and future chatbot/cloud phases and reside in `/specs/agents/skills/`.
- Agent and skill specs are written to be **reusable in future phases** (chatbot, cloud, etc.)—not limited to web implementation.

**Pattern:**  
To add or update a skill/agent, create or edit its markdown spec and reference in implementation.

---

## 💻 Technology Stack & Conventions

**Backend:**
- Python 3.13+, FastAPI, SQLModel, Neon PostgreSQL
- All REST routes under `/api/`
- JWT auth required for every endpoint (see specs)
- Project config in `pyproject.toml`, `uv.lock`
- ENV: Set `BETTER_AUTH_SECRET` for JWT signature verification

**Frontend:**
- Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Use `/lib/api.ts` as the single API client for backend interaction
- Prefer server components unless client-side interactivity is required

---

## ▶️ Setup & Running

**Backend:**
```bash
cd backend
uv venv
uv add fastapi sqlmodel psycopg[binary] python-dotenv
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Local Full-Stack (Docker, if configured):**
```bash
docker-compose up
```

---

## 🔐 Authentication Behavior

- Users register/sign in on the frontend (Better Auth issues JWT token).
- All API requests must include `Authorization: Bearer <token>`; backend rejects unauthenticated/invalid requests.
- API endpoints return or update only tasks belonging to the authenticated user, as enforced by JWT user ID.

---

## 🧩 Architectural Decisions

All major framework and workflow decisions are documented as ADRs in [`adr/`](./adr/).
Please review these records before proposing changes to architecture, stack, or specifications.

---


## 🔎 References & Help

- [Project overview](./specs/overview.md)
- [Task CRUD spec](./specs/features/task-crud.md)
- [Authentication spec](./specs/features/authentication.md)
- [REST API endpoints](./specs/api/rest-endpoints.md)
- [Database schema](./specs/database/schema.md)
- [Agents and subagents](./specys/agents/todo-agent.md)
- [Reusable agent skills](./specs/agents/skills/create-task.md)

---

### 📝 **Summary**
- All implementation strictly follows specs and this constitution.
- All code generation and structure is automated using Claude Code and Spec-Kit Plus.
- NO hand-written implementation code—only spec changes + automation.
- Agents, subagents, and skills are designed for max reusability across later phases and platforms.

---

- The Prompt Logger Agent records all user instructions in
 `.claude/   prompt-history.md`.