# ADR: Migrate MCP Tools to Phase 3 Backend API

**Date**: 2026-05-19
**Status**: Accepted

## Context

The Phase 4 Kubernetes deployment uses the Phase 3 backend (FastAPI with SQLModel)
but the MCP tools (create_todo, list_todos, delete_todo, update_todo, search_todos)
were still calling Phase 2 REST endpoints (`/api/{user_id}/tasks`).

Phase 3 changed the REST API to use `/tasks` (JWT-authenticated, resource-based) 
instead of `/api/{user_id}/tasks` (user-scoped). Additionally, Phase 3 uses 
PATCH instead of PUT for updates, and returns a different response shape 
(`{tasks: [...], total, page, page_size}` instead of `{tasks: [...], count}`).

## Decision

Update all 5 MCP tools to call Phase 3 endpoints:

| Tool | Old Endpoint | New Endpoint | Change |
|------|-------------|-------------|--------|
| create_todo | POST `/api/{uid}/tasks` | POST `/tasks` | Added priority/due_date support |
| list_todos | GET `/api/{uid}/tasks` | GET `/tasks` | Phase 3 response shape |
| update_todo | PUT `/api/{uid}/tasks/{id}` | PATCH `/tasks/{id}` | PUT→PATCH |
| delete_todo | GET/DELETE `/api/{uid}/tasks/{id}` | GET/DELETE `/tasks/{id}` | Endpoint path only |
| search_todos | GET `/api/{uid}/tasks/search?q=` | GET `/tasks?q=` | Unified into list endpoint |

## Consequences

- MCP tools now work with Phase 3 backend running in Minikube
- Chat command "add fee of june RS.5000" successfully creates tasks
- All 5 tools updated in `phase3-chatbot/backend/mcp_server/tools/`
- Backend image rebuilt with `--no-cache` and Helm upgrade deployed
