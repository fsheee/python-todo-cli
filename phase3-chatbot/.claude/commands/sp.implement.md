---
description: Execute Phase 3 implementation tasks (Phase 3 wrapper)
---

## Purpose

This is a Phase 3 wrapper for the Spec‑Kit Plus implementation command.

Because the repo-wide `sp.implement` command lives under `phase1-console/.claude/commands/`, this file makes the same command available when you are working **inside `phase3-chatbot/`**.

## What it does

1. Confirms the Phase 3 task file exists (`phase3-chatbot/specs/TASKS.md`).
2. Instructs you to run the implementation using the repo’s Spec‑Kit implementation flow.

## Preconditions

- Phase 3 plan exists: `phase3-chatbot/specs/PLAN.md`
- Phase 3 tasks exist: `phase3-chatbot/specs/TASKS.md`

## Implementation

This project currently stores Phase 3 tasks in `specs/TASKS.md` (uppercase), not `tasks.md`.
The upstream Spec‑Kit `sp.implement` command expects a `tasks.md` within a Spec‑Kit feature directory discovered by `.specify/scripts/powershell/check-prerequisites.ps1`.

So from Phase 3, the correct next action is to **execute the tasks in `specs/TASKS.md`**.

### Option A: Use the existing repo implementation command (recommended)

Run `/sp.implement` from the location where it is registered (repo currently has it in `phase1-console/.claude/commands/sp.implement.md`).

If your Claude Code session is scoped to `phase3-chatbot/` and cannot see that command, open a session at the repo root or `phase1-console/` and run `/sp.implement` there.

### Option B: If you want this command to be fully self-contained in Phase 3

Tell me, and I will update this command to:
- read `phase3-chatbot/specs/TASKS.md`
- drive execution phase-by-phase using the tasks listed there

(That would be a Phase 3–specific implementation runner rather than Spec‑Kit’s default `tasks.md` runner.)
