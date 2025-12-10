<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0
Bump rationale: MAJOR - Initial ratification of constitution with all core principles

Modified principles: N/A (initial version)
Added sections:
  - Core Principles (5 principles)
  - PHR (Prompt History Records)
  - ADR (Architecture Decision Records)
  - Project Structure
  - Governance

Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (Requirements align with principles)
  - .specify/templates/tasks-template.md: ✅ Compatible (Task structure supports principles)

Follow-up TODOs: None
-->

# Todo Phase I Constitution

## Core Principles

### I. Spec-Driven Development

Implement only features with a defined specification.

- Every feature MUST have a corresponding spec in `/specs/<feature>/spec.md` before implementation begins
- Specifications define inputs, actions, outputs, and constraints
- Code changes without a spec are prohibited
- If requirements change, update the spec first, then the implementation

**Rationale**: Specifications provide a single source of truth, prevent scope creep, and ensure all stakeholders share the same understanding of features.

### II. Smallest Viable Change

All code changes MUST be minimal and testable.

- Implement only what the spec defines—no additional features
- Each change MUST be independently verifiable
- Prefer small, focused commits over large sweeping changes
- Refactoring MUST be separated from feature work

**Rationale**: Small changes are easier to review, test, debug, and roll back. They reduce risk and accelerate feedback loops.

### III. Traceability (PHR)

Record all user prompts and code changes via Prompt History Records.

- Every significant interaction MUST generate a PHR in `history/prompts/`
- PHR routing:
  - Constitution-related → `history/prompts/constitution/`
  - Feature-related → `history/prompts/<feature-name>/`
  - General/misc → `history/prompts/general/`
- PHR MUST include:
  - User input (verbatim)
  - Assistant response (concise summary)
  - Stage and feature context

**Rationale**: Traceability enables learning, debugging, and auditing. PHRs create a searchable history of decisions and implementations.

### IV. Clean Code

Follow Python 3.13+ best practices with modular design.

- Functions MUST be single-purpose and independently testable
- Use clear, descriptive naming conventions
- Add docstrings for public functions and modules
- Keep functions short (< 20 lines preferred)
- Avoid deep nesting (max 3 levels)
- No global mutable state

**Rationale**: Clean code is maintainable, readable, and reduces cognitive load for future development.

### V. In-Memory Data

Store tasks in memory (list/dict) for Phase I.

- All task data MUST be stored in Python data structures (list or dict)
- No external databases, files, or persistence in Phase I
- Data is ephemeral—lost when the application exits
- Prepare data structures for future persistence layer (Phase II)

**Rationale**: In-memory storage simplifies Phase I development, allowing focus on core functionality without infrastructure complexity.

## PHR (Prompt History Records)

PHR captures the evolution of the project through user-assistant interactions.

### Routing Rules

| Stage | Route |
|-------|-------|
| constitution | `history/prompts/constitution/` |
| spec, plan, tasks, red, green, refactor, explainer, misc | `history/prompts/<feature-name>/` |
| general | `history/prompts/general/` |

### PHR Requirements

- Record user input verbatim
- Include assistant response (concise)
- Use proper stage and feature context
- Generate unique ID for each PHR

## ADR (Architecture Decision Records)

ADRs document significant architectural decisions.

### ADR Rules

- Detect and flag significant architectural decisions during development
- Suggest ADR creation with: `📋 Architectural decision detected: <brief>. Run /sp.adr <title>.`
- Do NOT auto-create ADRs; wait for user approval
- Store ADRs under `history/adr/`

### ADR Triggers

- Data structure choices (e.g., list vs dict for task storage)
- Storage method decisions
- API/CLI design patterns
- Third-party library selections

## Project Structure

```text
/src/                    - Source code (main.py entry point)
/tests/                  - Test files
/specs/                  - Feature specifications
/specs_history/          - Versioned specs archive
/history/prompts/        - PHR files
/history/adr/            - Architecture Decision Records
/README.md               - Setup instructions
/CLAUDE.md               - Claude Code instructions
/CONSTITUTION.md         - This file (symlink or reference)
```

## Governance

### Amendment Process

1. Propose change via `/sp.constitution` command
2. Document rationale for change
3. Update version following semantic versioning
4. Propagate changes to dependent templates
5. Record PHR for the amendment

### Versioning Policy

- **MAJOR**: Backward-incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review

- All implementation work MUST verify alignment with these principles
- Violations MUST be justified and documented in Complexity Tracking
- Constitution supersedes conflicting guidance in other documents

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06

