# Tasks: CLI Todo Application - Phase I

**Input**: Design documents from `/specs/001-cli-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/cli-commands.md

**Tests**: Tests are NOT explicitly requested in the spec. Test tasks are omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md in src/, src/models/, src/services/, src/cli/
- [X] T002 Initialize Python project with pyproject.toml for uv package manager
- [X] T003 [P] Create src/__init__.py with package docstring
- [X] T004 [P] Create src/models/__init__.py
- [X] T005 [P] Create src/services/__init__.py
- [X] T006 [P] Create src/cli/__init__.py
- [X] T007 [P] Create custom exceptions in src/exceptions.py (TaskNotFoundError, ValidationError, InvalidIdError)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Create Task dataclass in src/models/task.py with id, title, description, is_complete fields
- [X] T009 Create TaskService class skeleton in src/services/task_service.py with _tasks dict and _next_id counter
- [X] T010 Implement get_all() method in src/services/task_service.py returning list of all tasks
- [X] T011 Create CLI menu display function in src/cli/commands.py
- [X] T012 Create main entry point in src/main.py with menu loop and exit handling

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Display all tasks with ID, title, description, and status indicators

**Independent Test**: Run app → select option 1 → verify tasks display with status indicators or "No tasks" message

### Implementation for User Story 1

- [X] T013 [US1] Implement view_tasks() CLI handler in src/cli/commands.py with formatted table output
- [X] T014 [US1] Add status indicators ([ ] / [X]) to task display in src/cli/commands.py
- [X] T015 [US1] Handle empty task list case with "No tasks found" message in src/cli/commands.py
- [X] T016 [US1] Add task count summary (total, complete, incomplete) to view output in src/cli/commands.py
- [X] T017 [US1] Wire view command (option 1) to menu loop in src/main.py

**Checkpoint**: User Story 1 complete - can view tasks (empty list shows message)

---

## Phase 4: User Story 2 - Add New Task (Priority: P1) 🎯 MVP

**Goal**: Allow users to add tasks with title and optional description

**Independent Test**: Run app → add task with title/description → view tasks → verify new task appears with unique ID

### Implementation for User Story 2

- [X] T018 [US2] Implement add_task(title, description) method in src/services/task_service.py with auto-increment ID
- [X] T019 [US2] Add title validation (non-empty) in src/services/task_service.py raising ValidationError
- [X] T020 [US2] Implement add_task_command() CLI handler in src/cli/commands.py with input prompts
- [X] T021 [US2] Handle validation errors with user-friendly messages in src/cli/commands.py
- [X] T022 [US2] Wire add command (option 2) to menu loop in src/main.py

**Checkpoint**: User Stories 1 & 2 complete - MVP functional (add + view)

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Toggle task completion status by ID

**Independent Test**: Add task → toggle complete → view (shows [X]) → toggle again → view (shows [ ])

### Implementation for User Story 3

- [X] T023 [US3] Implement get_task(id) method in src/services/task_service.py returning Task or None
- [X] T024 [US3] Implement toggle_complete(id) method in src/services/task_service.py
- [X] T025 [US3] Implement toggle_command() CLI handler in src/cli/commands.py with ID input
- [X] T026 [US3] Handle TaskNotFoundError with user-friendly message in src/cli/commands.py
- [X] T027 [US3] Handle InvalidIdError for non-numeric input in src/cli/commands.py
- [X] T028 [US3] Wire toggle command (option 5) to menu loop in src/main.py

**Checkpoint**: User Story 3 complete - can toggle task completion status

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Update task title and/or description by ID

**Independent Test**: Add task → update title → view (shows new title) → update description → view (shows new description)

### Implementation for User Story 4

- [X] T029 [US4] Implement update_task(id, title, description) method in src/services/task_service.py
- [X] T030 [US4] Add title validation for updates (non-empty if provided) in src/services/task_service.py
- [X] T031 [US4] Implement update_command() CLI handler in src/cli/commands.py with optional field inputs
- [X] T032 [US4] Handle "keep current" behavior (empty input) in src/cli/commands.py
- [X] T033 [US4] Wire update command (option 3) to menu loop in src/main.py

**Checkpoint**: User Story 4 complete - can update task details

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Remove task by ID

**Independent Test**: Add task → delete by ID → view (task no longer appears)

### Implementation for User Story 5

- [X] T034 [US5] Implement delete_task(id) method in src/services/task_service.py returning bool
- [X] T035 [US5] Implement delete_command() CLI handler in src/cli/commands.py with ID input
- [X] T036 [US5] Handle TaskNotFoundError with user-friendly message in src/cli/commands.py
- [X] T037 [US5] Wire delete command (option 4) to menu loop in src/main.py

**Checkpoint**: All user stories complete - full feature set implemented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T038 Add input validation helper function for ID parsing in src/cli/commands.py
- [X] T039 Add consistent error message formatting in src/cli/commands.py
- [X] T040 Add docstrings to all public functions in src/models/task.py
- [X] T041 Add docstrings to all public methods in src/services/task_service.py
- [X] T042 Add docstrings to all CLI handlers in src/cli/commands.py
- [X] T043 Run manual validation using quickstart.md scenarios
- [X] T044 Verify all edge cases from spec.md are handled

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - View tasks
- **User Story 2 (Phase 4)**: Depends on Foundational - Add tasks (can parallel with US1)
- **User Story 3 (Phase 5)**: Depends on Foundational + US2 (needs tasks to toggle)
- **User Story 4 (Phase 6)**: Depends on Foundational + US2 (needs tasks to update)
- **User Story 5 (Phase 7)**: Depends on Foundational + US2 (needs tasks to delete)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```text
Phase 1: Setup
    ↓
Phase 2: Foundational
    ↓
    ├── Phase 3: US1 View (P1) ──┐
    │                            │
    └── Phase 4: US2 Add (P1) ───┼──▶ MVP Complete
                                 │
                    ┌────────────┘
                    ↓
            Phase 5: US3 Toggle (P2)
                    ↓
            Phase 6: US4 Update (P3)
                    ↓
            Phase 7: US5 Delete (P3)
                    ↓
            Phase 8: Polish
```

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006, T007 can all run in parallel

**Phase 3 & 4 (US1 + US2)**:
- Can be developed in parallel since both only depend on Foundational phase

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all init files in parallel:
Task: "Create src/__init__.py with package docstring"
Task: "Create src/models/__init__.py"
Task: "Create src/services/__init__.py"
Task: "Create src/cli/__init__.py"
Task: "Create custom exceptions in src/exceptions.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View)
4. Complete Phase 4: User Story 2 (Add)
5. **STOP and VALIDATE**: Test add + view workflow
6. Deploy/demo MVP if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (View) + US2 (Add) → MVP! (can demo basic workflow)
3. Add US3 (Toggle) → Can track completion status
4. Add US4 (Update) → Can modify tasks
5. Add US5 (Delete) → Can remove tasks
6. Polish → Production-ready

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Setup | 7 | Project structure, init files, exceptions |
| Foundational | 5 | Task model, service skeleton, menu, main |
| US1 View | 5 | View tasks with status indicators |
| US2 Add | 5 | Add tasks with validation |
| US3 Toggle | 6 | Toggle completion status |
| US4 Update | 5 | Update task details |
| US5 Delete | 4 | Delete tasks |
| Polish | 7 | Docstrings, validation, edge cases |
| **Total** | **44** | |

### Parallel Opportunities

- Phase 1: 5 tasks parallelizable
- Phase 3 + 4: Can run in parallel (independent user stories)

### MVP Scope

- **Minimum**: Phase 1 + 2 + 3 + 4 (22 tasks)
- **Full**: All phases (44 tasks)

---

## Notes

- [P] tasks = different files, no dependencies
- [US#] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included (not requested in spec) - add if needed later
