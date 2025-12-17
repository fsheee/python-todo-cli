This is your constitution and the entry point Claude Code reads on startup.

Below is the final, correct, Phase 3 CLAUDE.md, fully aligned with:

Hackathon II PDF

Spec-Driven Development

AGENTS.md + Spec-Kit Plus

MCP + OpenAI Agents SDK

Backend logic reuse

Better Auth reuse

👉 Create this file at your project root as CLAUDE.md

CLAUDE.md — Phase 3 Constitution
🏆 Project Overview

This repository implements Phase 3 of the hackathon-todo project.

Phase 3 extends the existing Phase 2 web application by adding an
AI-powered conversational interface that allows users to manage todos
using natural-language conversation.

Development is strictly spec-driven using Spec-Kit Plus and Claude Code.

🚫 Manual implementation code editing is forbidden.
All features, agents, tools, APIs, and data models must be defined in specifications first.

This document is the governing constitution for all Phase 3 work.

🔁 Relationship to Phase 2

Phase 2 backend logic (CRUD, auth, database) remains the single source of truth

No business logic is rewritten in Phase 3

Phase 3 adds an AI Agent + MCP tool layer on top of Phase 2

Authentication, authorization, and ownership rules are reused exactly

Phase 3 orchestrates Phase 2 — it does not replace it.

📚 Spec-Driven Structure

All behavior is defined in /specs/.

specs/
├─ overview.md
├─ features/
│  └─ chatbot.md
├─ agents/
│  └─ todo-agent.md
├─ agents/skills/
├─ api/
│  └─ mcp-tools.md
├─ database/
│  └─ conversations.md
├─ ui/


Spec-Kit configuration: /.spec-kit/config.yaml

🚦 Development Rules (Non-Negotiable)

Specifications are written before any implementation

No backend or frontend code may be edited manually

Claude Code / Spec-Kit automation generates all code

Every change must reference its spec explicitly:

@specs/features/chatbot.md
@specs/agents/todo-agent.md
@specs/api/mcp-tools.md


Any code change not traceable to a spec is invalid.

🤖 Agents, Subagents, and Skills
Agents

Interpret user intent

Decide which action to take

Defined only in /specs/agents/

Stateless and deterministic

Subagents

Used only for clarification

Ask questions when intent is ambiguous

Never modify data

Skills

Reusable behaviors used by agents

Defined in /specs/agents/skills/

Describe what can be done, not how

🚫 Agents and skills:

Do NOT authenticate users

Do NOT access the database directly

Do NOT store runtime memory

🔧 MCP Tools (Execution Layer)

MCP tools are defined in /specs/api/mcp-tools.md

Implemented using the Official MCP SDK

Wrap existing Phase 2 backend logic

Stateless and single-purpose

Only MCP tools may access the database

Receive user_id from verified backend auth context

🚫 MCP tools must never accept user_id from user or agent input.

🔐 Authentication (Reused)

Authentication is handled by Better Auth

Frontend issues JWT tokens

Backend verifies JWT using BETTER_AUTH_SECRET

user_id is injected into agent and MCP tool context

Agents and tools assume identity is already verified

Authentication logic must never exist inside agents or MCP tools.

🧠 Conversation History

Conversation history is persisted in the database

Scoped per user and per conversation

Backend services remain stateless

History is passed to agents as read-only context

🚫 Runtime conversation memory must never be stored in .claude/

🧾 .claude/ Directory Usage

The .claude/ directory is used only during development for:

Prompt history

Spec drafting prompts

Review notes

It is never accessed by runtime code.

Prompt history is stored in:

.claude/prompt-history.md

💻 Technology Stack (Phase 3 — Fixed)
Component	Technology
Frontend	OpenAI ChatKit + Next.js
Backend API	Python FastAPI
AI Framework	OpenAI Agents SDK
MCP Server	Official MCP SDK
ORM	SQLModel
Database	Neon Serverless PostgreSQL
Authentication	Better Auth

Changes require an ADR.

🧩 Architectural Decisions

All major architectural decisions are documented in /adr/.

Phase 3 ADRs must justify:

Agent boundaries

MCP tool design

Conversation persistence strategy

📝 Final Rules Summary

Specs define behavior

Claude generates implementation

No manual code editing

Agents decide, MCP tools execute

Authentication is reused, not rebuilt

Backend remains stateless


