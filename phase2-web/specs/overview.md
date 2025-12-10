# Todo App Overview

## Objective

Transform the Phase 1 in-memory console todo app into a modern, multi-user web application with persistent storage, powered by spec-driven development using Claude Code and Spec-Kit Plus.

---

## Requirements (Phase II)

- Implement all 5 core Basic Level features as a web application:
  - Add Task
  - Delete Task
  - Update Task
  - View Task List
  - Mark as Complete
- Create RESTful API endpoints for all task operations.
- Build a responsive, user-friendly frontend interface.
- Store all app data in Neon Serverless PostgreSQL database.
- Add secure user authentication (signup/signin) with Better Auth.
- **Introduce reusable agents, subagents, and skills in specs for future intelligent, AI, and cloud features.**
- Automatically log all user prompts via a Prompt Agent for audit, context reuse, and collaboration.

---

## Technology Stack

| Layer       | Technology                    |
|-------------|------------------------------|
| Frontend    | Next.js 16+ (App Router)     |
| Backend     | Python FastAPI               |
| ORM         | SQLModel                     |
| Database    | Neon Serverless PostgreSQL   |
| Spec-Driven | Claude Code + Spec-Kit Plus  |
| Auth        | Better Auth (JWT-based)      |

---

### REST API Endpoints


| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create a new task |
| GET | /api/{user_id}/tasks/{id} | Get task details |
| PUT | /api/{user_id}/tasks/{id} | Update a task |
| DELETE | /api/{user_id}/tasks/{id} | Delete a task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle task completion |




*All endpoints require authentication via JWT token.*

---

## Authentication & Security

### Better Auth + FastAPI (JWT Workflow)

- Users authenticate via Better Auth; frontend receives a JWT token.
- The token is attached to all API requests in the `Authorization: Bearer <token>` header.
- FastAPI backend uses shared secret to verify JWT, extract user info, and filter data.
- Only authenticated users can view or modify their own tasks.

**Security Benefits:**
- User isolation: no cross-account data access
- Stateless authentication: no server-side sessions needed
- Automatic token expiry
- API remains simple and RESTful

---

## Agents, Subagents & Skills (For Reusability & Future Phases)

- **Agents:** Modular automations orchestrating tasks, authentication, and user flows.
- **Subagents:** Specialized micro-bots for focused flows (e.g., CRUD, completion toggle).
- **Skills:** Reusable behaviors (e.g., create-task, verify-jwt) usable by agents in web, chatbot, and cloud phases.
- **Prompt Agent:** Automatically logs all user prompts to `.claude/prompt-history.md` for audit trail, collaboration, and reusability in future phases.

Specs for agents and skills are organized in `/specs/agents/` and `/specs/agents/skills/` so they can be reused and extended in later phases (AI chatbot, Kubernetes, etc).

---

## Summary

Phase II delivers a secure, spec-driven, full-stack todo application:
- Multi-user support with authentication.
- Persistent task storage.
- Clean, responsive web UI.
- All business logic defined in structured, reusable specs for easy automation, intelligent features, prompt history auditing, and future cloud-native enhancements.