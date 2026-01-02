---
id: PHR-001
title: constitution-initial-ratification
stage: constitution
date: 2025-12-06
surface: claude-code
model: claude-sonnet-4-5-20250929
feature: constitution
branch: master
user: architect
command: /sp.constitution
labels: [constitution, governance, initial-setup]
links:
  spec: N/A
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: .specify/memory/constitution.md
    action: created
tests:
  - N/A
---

## Prompt

```yaml
# sp.constitution
name: todo_phase1_constitution
description: "Core rules, principles, and workflow for Phase I Todo App using Claude Code and Spec-Kit Plus."

# Core Principles
principles:
  - "Spec-Driven Development: Implement only features with a defined spec."
  - "Smallest Viable Change: All code changes must be minimal and testable."
  - "Traceability: Record all user prompts and code changes (PHR)."
  - "Clean Code: Follow Python 3.13+ best practices with modular design."
  - "In-Memory Data: Store tasks in memory (list/dict) for Phase I."

# PHR (Prompt History Records)
phr:
  route:
    constitution: "history/prompts/constitution/"
    feature: "history/prompts/<feature-name>/"
    general: "history/prompts/general/"
  rules:
    - "Record user input verbatim."
    - "Include assistant response."
    - "Use proper stage and feature context."

# ADR (Architecture Decision Records)
adr:
  rules:
    - "Detect and flag significant architectural decisions."
    - "Suggest ADR creation: '📋 Architectural decision detected: <brief>. Run `/sp.adr <title>`.'"
    - "Do not auto-create ADRs; wait for user approval."
    - "Store ADRs under history/adr/"

# Project Structure
structure:
  src: "/sr/specs_history/ - Versioned specs"
  readme: "/README.md - Setup instructions"
  claude: "/CLAUDE.md - Claude Code instructions"
  constitution: "/CONSTITUTION.md - Principles & rules"
  prompts: "/history/prompts/ - PHRs"
  adr: "/history/adr/ - Architecture Decisions"
```

## Response snapshot

Created Todo Phase I Constitution v1.0.0 with:

- **5 Core Principles**: Spec-Driven Development, Smallest Viable Change, Traceability (PHR), Clean Code, In-Memory Data
- **PHR Section**: Routing rules and requirements for prompt history records
- **ADR Section**: Rules and triggers for architecture decision records
- **Project Structure**: Defined directory layout for the project
- **Governance**: Amendment process, versioning policy, and compliance review

All templates validated as compatible:
- plan-template.md: Constitution Check section exists
- spec-template.md: Requirements align with principles
- tasks-template.md: Task structure supports principles

## Outcome

- ✅ Impact: Initial constitution ratified, establishing governance framework for Phase I
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created)
- 🔁 Next prompts: Begin feature specification with /sp.specify
- 🧠 Reflection: Constitution provides clear boundaries for Phase I scope (in-memory only) and enforces spec-driven development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
