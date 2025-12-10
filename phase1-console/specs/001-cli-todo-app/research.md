# Research: CLI Todo Application - Phase I

**Feature**: 001-cli-todo-app
**Date**: 2025-12-06
**Status**: Complete

## Research Questions

### RQ-001: Data Structure for Task Storage

**Question**: Should tasks be stored in a list or dictionary?

**Decision**: Dictionary (dict) with task ID as key

**Rationale**:
- O(1) lookup by ID for get/update/delete operations
- O(n) for listing all tasks (acceptable for Phase I)
- Natural mapping: ID → Task object
- Supports future persistence layer (dict serializes to JSON easily)

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| List | Simple iteration, ordered | O(n) lookup by ID | Rejected |
| Dict | O(1) lookup, ID-based access | Slightly more complex | **Selected** |
| OrderedDict | Preserves insertion order | Unnecessary overhead | Rejected |

### RQ-002: ID Generation Strategy

**Question**: How should unique task IDs be generated?

**Decision**: Auto-incrementing integer counter

**Rationale**:
- Simple to implement and understand
- Guaranteed uniqueness within session
- User-friendly (short numeric IDs)
- Matches spec assumption: "Task IDs are positive integers starting from 1"

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Auto-increment | Simple, sequential, readable | Resets on restart | **Selected** |
| UUID | Globally unique | Long, unfriendly for CLI | Rejected |
| Timestamp-based | Unique, sortable | Less readable | Rejected |

### RQ-003: CLI Interface Pattern

**Question**: What CLI interface pattern should be used?

**Decision**: Interactive menu-driven loop

**Rationale**:
- Matches user expectations for a todo app
- Allows multiple operations without restarting
- Simple to implement with stdlib (input/print)
- No external dependencies required

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Interactive menu | Intuitive, multiple ops | Requires loop management | **Selected** |
| Argparse commands | Standard CLI pattern | One op per invocation | Rejected |
| Click/Typer | Rich CLI features | External dependency | Rejected |

### RQ-004: Task Model Implementation

**Question**: How should the Task entity be modeled?

**Decision**: Python dataclass

**Rationale**:
- Clean, minimal boilerplate
- Built-in `__init__`, `__repr__`, `__eq__`
- Type hints for clarity
- Immutable option available (frozen=True) if needed
- Part of Python stdlib (no dependencies)

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| dataclass | Clean, type-safe, stdlib | None significant | **Selected** |
| Plain dict | Flexible | No type safety | Rejected |
| NamedTuple | Immutable | Less readable | Rejected |
| Pydantic | Validation | External dependency | Rejected |

### RQ-005: Error Handling Strategy

**Question**: How should errors be handled and displayed?

**Decision**: Custom exception classes with user-friendly messages

**Rationale**:
- Separation of concerns (service raises, CLI catches and displays)
- Consistent error format for users
- Testable error conditions
- Follows Clean Code principle

**Alternatives Considered**:
| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Custom exceptions | Clean separation, testable | More code | **Selected** |
| Return codes | Simple | Hard to distinguish errors | Rejected |
| Print in service | Quick | Couples UI to logic | Rejected |

## Technology Decisions Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Storage | Dict with ID keys | O(1) lookup |
| ID Generation | Auto-increment int | Simple, readable |
| CLI Pattern | Interactive menu | Multi-op support |
| Task Model | dataclass | Clean, stdlib |
| Error Handling | Custom exceptions | Testable, clean separation |

## Dependencies

**Production**: None (stdlib only)

**Development**:
- pytest (testing)
- uv (package management)

## Unresolved Questions

None - all technical decisions resolved for Phase I scope.
