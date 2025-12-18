# AGENTS.md — Phase 3 Agent Definitions

This file defines all agents, subagents, and skills used in Phase 3 of the hackathon-todo project.  
It complements CLAUDE.md by providing a clear reference for Phase 3 AI orchestration.

## Agents Overview

| User Intent                     | MCP Tool Called         | Output                            |
|---------------------------------|------------------------ |------------------------------------|
| Add a new todo                  | create_todo_tool        | Success message, updated todo list |
| Update existing todo            | update_todo_tool       | Updated todo details                |
| Delete a todo                   | delete_todo_tool       | Deletion confirmation               |
| List todos                      | list_todos_tool        | Current todos for user              | 

## Agent Types

### 1. Agents

- **Interpret user intent** and decide which action to take  
- Stateless and deterministic  
- Do **not** authenticate users or access database directly  
- Only call **MCP tools** to execute actions

### 2. Subagents

- Used for clarification when user input is ambiguous  
- Never modify data  
- Always return questions or recommendations to the main agent

### 3. Skills

- Reusable behaviors used by agents  
- Describe what can be done, not how  
- Defined under `/specs/agents/skills/`  
- Examples:
  - `parse_todo_intent`: parse user prompt into actionable task
  - `summarize_conversation`: provide a summary of conversation history
  - `validate_input`: ensure input is suitable for MCP execution

## MCP Tool Interaction

All agents rely on **MCP tools** for execution. MCP tools:

- Wrap existing Phase 2 backend logic (CRUD, auth, database access)  
- Receive verified `user_id` from backend context  
- Are stateless and single-purpose  
- Never receive `user_id` from user or agent input  

**Todo-Agent → MCP Tools Example:**

| User Intent                     | MCP Tool Called         | Output |
|---------------------------------|------------------------|--------|
| Add a new todo                  | create_todo_tool       | Success message, updated todo list |
| Update existing todo             | update_todo_tool       | Updated todo details |
| Delete a todo                    | delete_todo_tool       | Deletion confirmation |
| List todos                       | list_todos_tool        | Current todos for user |

## Conversation Context

- Agents always receive **read-only conversation history**  
- History is **per user, per conversation**  
- Runtime memory is **never stored in `.claude/`**  

## Best Practices

- Always use MCP tools for all actions  
- Never store secrets or credentials  
- Stateless: do not retain any runtime data  
- Ask clarifying questions if intent is ambiguous  
- Reuse skills wherever possible to avoid duplication  

## Folder Structure Reference
specs/
├─ agents/
│ └─ todo-agent.md
├─ agents/skills/
│ ├─ parse_todo_intent.md
│ ├─ summarize_conversation.md
│ └─ validate_input.md
