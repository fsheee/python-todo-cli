# Claude Code Rules


You are an expert AI assistant specializing in Spec-Driven Development (SDD). Your primary goal is to work with the architext to build products.

# Todo App - Phase I Claude Code Guide

## Overview
This project uses **Claude Code** and **Spec-Kit Plus** for spec-driven development (SDD).  
Phase I is an in-memory Python console application implementing the 5 basic todo features:
- Add Task
- Delete Task
- Update Task
- View Tasks
- Mark Task Complete/Incomplete

All development must strictly follow specifications defined in `/specs` and use Claude Code workflows.

---

## Setup

1. **Python Version:** 3.13+
2. **Dependency Manager:** uv

Add dependencies (if any):
```bash
uv add


Iterate

Update the spec if the feature changes.

Store all spec versions in /specs_history for traceability.

Guideline Workflow

Follow these steps for each feature or task:

Read the Spec

Navigate to /specs/<feature>/spec.md.

Understand the inputs, actions, outputs, and constraints.

Plan Implementation

Break the feature into small functions.

Identify data structures (in-memory list/dict for Phase I).

Consider error paths and edge cases.

Implement Code

Only implement what the spec defines.

Keep functions modular and reusable.

Add docstrings and comments for clarity.

Test Feature

Run the app via uv run src/main.py.

Verify all outputs and status indicators.

Test error handling (invalid inputs, missing task IDs, etc.).

Record PHR (Prompt History Record)

Every user action or implementation step must generate a PHR in history/prompts/.

Include full input, output, and context.

Route files to appropriate directories: constitution, <feature-name>, or general.

Iterate / Refactor

If the feature doesn’t fully meet the spec, update the code or spec.

Record any changes in /specs_history.

ADR Check

If the feature introduces an architectural decision (data structure choice, storage method, API design), create a suggested ADR:

📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <decision-title>`


Wait for user consent before creating ADRs.


