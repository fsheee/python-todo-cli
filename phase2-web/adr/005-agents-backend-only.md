# ADR-005: Agents and Skills - Backend Only

**Status:** Accepted
**Date:** 2025-12-11
**Decision Makers:** Claude, User

---

## Context

The project uses an agent/skill pattern for organizing backend logic. Clarification was needed on whether agents/skills should exist in the frontend.

## Decision

**Agents and skills are backend-only concepts.**

- Frontend makes HTTP calls to REST API
- Backend internally uses agent/skill pattern
- No agent code in frontend
- Specs in `/specs/agents/` are for backend architecture documentation

## Architecture

```
Frontend (Next.js)          Backend (FastAPI)
─────────────────          ─────────────────
src/
├── app/                   routes/
├── components/            ├── auth.py
├── lib/                   └── tasks.py ← agent pattern
│   └── api.ts  ────────►
└── types/                 specs/agents/ ← documentation only
                           ├── todo-agent.md
                           └── skills/
```

## Rationale

### Why Backend Only?
- Agents orchestrate business logic - belongs on server
- Frontend is purely presentational
- Keeps frontend thin and focused on UI
- Security - sensitive logic stays server-side

### Frontend Role
- Call REST API endpoints
- Handle UI state and rendering
- Display data from backend
- No business logic

### Backend Agent Pattern
- Todo Agent orchestrates task operations
- Skills are atomic operations (create, list, update, delete)
- Agents delegate to skills
- Skills interact with database

## Consequences

### Positive
- Clear separation of concerns
- Frontend remains simple
- Backend logic is testable
- Easy to add new clients (mobile, CLI)

### Negative
- All logic changes require backend deployment
- Cannot do offline-first features easily

## Related Specs
- `/specs/agents/todo-agent.md`
- `/specs/agents/skills/*.md`

---
