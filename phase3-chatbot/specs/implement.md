# Phase 3 Implementation Wrapper (Spec-Kit Plus)

This document describes how to execute **Phase 3** implementation using the existing Spec‑Kit Plus workflow.

> Note: In this repository, the `sp.implement` command is defined under `phase1-console/.claude/commands/sp.implement.md`.
> That command expects Spec‑Kit’s *feature directory* layout (including `plan.md` and `tasks.md`) as discovered by
> `.specify/scripts/powershell/check-prerequisites.ps1`.

## Preconditions

- You are in the **repo root**: `F:\claude-code\hackathon-todo`
- PowerShell is available (`pwsh`)
- Your Phase 3 spec set is complete (see `phase3-chatbot/specs/PLAN.md`)

## What this wrapper does

1. Uses Spec‑Kit’s prerequisite script to determine the current `FEATURE_DIR`.
2. Verifies `plan.md` exists.
3. Verifies `tasks.md` exists (or tells you to generate it first).
4. Then you can run the implementation command (`/sp.implement`) to execute tasks phase-by-phase.

## Step 1: Determine the feature directory (FEATURE_DIR)

Run the prerequisite checker **from repo root** (the script is currently located under `phase1-console/.specify/`):

```powershell
pwsh -File "phase1-console/.specify/scripts/powershell/check-prerequisites.ps1" -Json -RequireTasks -IncludeTasks
```

This prints JSON including:
- `FEATURE_DIR`
- `AVAILABLE_DOCS` (should include `tasks.md` when present)

## Step 2: If `tasks.md` is missing, generate tasks

If the prerequisite checker reports `tasks.md not found`, you must generate a task breakdown before implementation.

Typical Spec‑Kit flow:
- Create/update the plan
- Generate tasks from the plan

In Claude Code, that is usually:
- `/sp.tasks`

(Use the repo’s Spec‑Kit commands you have available; this repo stores commands under `.claude/commands/` in feature folders.)

## Step 3: Run implementation

Once `tasks.md` exists in `FEATURE_DIR`, run:

- `/sp.implement`

It will:
- Check any `checklists/` (and stop for confirmation if incomplete)
- Read `tasks.md` + `plan.md` (+ optional docs)
- Execute tasks phase-by-phase
- Mark completed tasks as `[X]` in the tasks file

## Phase 3 scope reminders

Phase 3’s plan (`phase3-chatbot/specs/PLAN.md`) covers:
- FastAPI backend `/chat` endpoint and auth middleware usage
- OpenAI Agent integration + tool routing
- MCP server tools (`create_todo`, `list_todos`, `update_todo`, `delete_todo`, `search_todos`)
- Chat history persistence
- Frontend chat UI integration

Important constraints (see `phase3-chatbot/CLAUDE.md`):
- Phase 3 orchestrates Phase 2; it does not rewrite Phase 2 CRUD/auth.
- Identity comes from validated JWT; MCP tools must not accept user_id from user input.

## Troubleshooting

- If `FEATURE_DIR` points to the wrong area, verify which branch/feature Spec‑Kit thinks is active.
- If you can’t run `/sp.implement` from repo root, you may need to run it from the folder where the command is registered (currently `phase1-console/`), or copy/link the command into the root `.claude/commands/`.
