
## Claude Code Rules

## Project Overview

This repository implements Phase 3 of the hackathon-todo project.

Phase 3 extends the existing Phase 2 web application by adding an
AI-powered conversational interface that allows users to manage todos
using natural-language conversation.

Development is strictly spec-driven using Spec-Kit Plus and Claude Code.

🚫 Manual implementation code editing is forbidden.
All features, agents, tools, APIs, and data models must be defined in specifications first.

This document is the governing constitution for all Phase 3 work.

🔁 Relationship to Phase 2

Phase 3 does **not rewrite or replace Phase 2 backend logic**.  
All existing Phase 2 **CRUD logic, authentication, authorization, and database schemas** are reused exactly.  

Phase 3 adds an **AI Agent + MCP tool layer** on top of the Phase 2 backend.  

**Better Auth is fully reused:**
- Frontend issues JWT tokens.  
- Backend verifies tokens using `BETTER_AUTH_SECRET`.  
- Agents and MCP tools receive **verified `user_id`** from backend; they do **not** handle authentication themselves.  

**Key principle:** Phase 3 orchestrates Phase 2; **no business logic is rewritten**.

📚 Spec-Driven Structure

All behavior is defined in `/specs/`:
specs/
├─ overview.md
├─ features/
│ └─ chatbot.md
├─ agents/
│ └─ todo-agent.md
├─ agents/skills/
├─ api/
│ └─ mcp-tools.md
├─ database/
│ └─ conversations.md
├─ ui/


Spec-Kit configuration: `/.spec-kit/config.yaml`

🚦 Development Rules (Non-Negotiable)

- Specifications are written before any implementation.
- No backend or frontend code may be edited manually.
- Claude Code / Spec-Kit automation generates all code.
- Every change must reference its spec explicitly:



@specs/features/chatbot.md
@specs/agents/todo-agent.md
@specs/api/mcp-tools.md


- Any code change not traceable to a spec is invalid.

🤖 Agents, Subagents, and Skills

**Agents:**  
- Interpret user intent  
- Decide which action to take  
- Stateless and deterministic  

**Subagents:**  
- Ask clarifying questions when intent is ambiguous  
- Never modify data  

**Skills:**  
- Reusable behaviors used by agents  
- Stateless, read-only, no direct database access  

🔧 MCP Tools (Execution Layer)

- Defined in `/specs/api/mcp-tools.md`  
- Implemented using the Official MCP SDK  
- Wrap existing Phase 2 backend logic  
- Only MCP tools may access the database  
- Receive `user_id` from verified backend auth context  
- Never accept `user_id` from user or agent input  

🔐 Authentication (Reused)

- Phase 3 **does not implement authentication**.  
- Authentication is handled by **Better Auth** (Phase 2).  
- Agents and MCP tools assume identity is already verified.  
- **Never store secrets or auth logic** in agents or MCP tools.  

🧠 Conversation History

- Persisted in database, scoped per user and conversation  
- Read-only context passed to agents  
- Runtime memory must never be stored in `.claude/`  

🧾 .claude/ Directory Usage

- Used only for development: prompt history, spec drafts, notes  
- Never accessed by runtime code  

💻 Technology Stack (Phase 3)

| Component       | Technology                         |
|-----------------|-----------------------------------|
| Frontend        | OpenAI ChatKit + Next.js           |
| Backend API     | Python FastAPI                     |
| AI Framework    | OpenAI Agents SDK                  |
| MCP Server      | Official MCP SDK                   |
| ORM             | SQLModel                           |
| Database        | Neon Serverless PostgreSQL         |
| Authentication  | Better Auth                        |

🧩 Architectural Decisions

- All major decisions documented in `/adr/`  
- Must justify agent boundaries, MCP tool design, conversation persistence  

📝 Final Rules Summary

- Specs define behavior  
- Claude generates implementation  
- No manual code editing  
- Agents decide, MCP tools execute  
- Authentication is reused, not rebuilt  
- Backend remains stateless  

## Core Guarantees (Product Promise)

- Record every user input verbatim in a Prompt History Record (PHR)  
- PHR routing (all under `history/prompts/`):



Constitution → history/prompts/constitution/
Feature → history/prompts/<feature-name>/
General → history/prompts/general/


- ADR suggestions surfaced intelligently, user consent required  

## Development Guidelines

1. **Authoritative Source Mandate:** Always use MCP tools and CLI commands for execution.  
2. **Execution Flow:** MCP servers are first-class tools; avoid internal assumptions.  
3. **PHR Capture:** Every user input creates a Prompt History Record.  
4. **Explicit ADR Suggestions:** Significant architectural decisions trigger ADR prompts.  
5. **Human-in-the-Loop:** Ask for user input when requirements are ambiguous or trade-offs exist.  

## Execution Contract for Every Request

1. Confirm surface and success criteria.  
2. List constraints, invariants, non-goals.  
3. Produce artifact with acceptance checks.  
4. Add follow-ups and risks (max 3).  
5. Create PHR in appropriate directory.  
6. Surface ADR suggestions if significant.  

## Minimum Acceptance Criteria

- Clear, testable acceptance criteria  
- Explicit error paths and constraints  
- Smallest viable change  
- Code references for modified/inspected files  

## Architect Guidelines

- Scope, dependencies, interfaces, NFRs, data management, operational readiness, risks, validation  
- ADR suggested when long-term impact exists  

## Basic Project Structure

- `.specify/memory/constitution.md` — Project principles  
- `specs/<feature>/spec.md` — Feature requirements  
- `specs/<feature>/plan.md` — Architecture decisions  
- `specs/<feature>/tasks.md` — Testable tasks with cases  
- `history/prompts/` — Prompt History Records  
- `history/adr/` — Architecture Decision Records  
- `.specify/` — SpecKit Plus templates and scripts  

## Active Technologies

- Python 3.13+ (backend) + FastAPI, SQLModel, MCP SDK, OpenAI Agents SDK  
- TypeScript/Node.js 22+ (frontend) + Next.js 16, @openai/chatkit  
- Neon Serverless PostgreSQL  

## Recent Changes

- Phase 3: Added AI conversational interface, agents, MCP tools, and spec-driven automation.  
- Full reuse of Phase 2 backend logic and Better Auth.
