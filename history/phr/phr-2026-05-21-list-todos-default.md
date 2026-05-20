# PHR: list_todos Default Status Returns No Results

**Date**: 2026-05-21
**Status**: Completed

## Problem Statement

The `show all task which have been store in DB` command returned "I could not find any tasks in the database" even though tasks existed. The issue was in the `list_todos` MCP tool defaulting to `status="pending"` instead of `status="all"`.

### Impact
- **High**: Users couldn't see their existing tasks via natural language commands
- Only tasks with `status="pending"` were returned, while completed or other-status tasks were hidden

### Context
- The `list_todos` function signature: `list_todos(user_id, status="pending")`
- The LLM didn't always pass `status="all"` in its tool call
- Multiple tools (both `backend/mcp_server/tools/list_todos.py` and `mcp_server/tools/list_todos.py`) had the same issue

---

## Hypothesis

The `status` parameter default was `"pending"`, so when the LLM or command parser called `list_todos` without specifying status, only pending tasks were returned. Changing the default to `"all"` would return all tasks regardless of status.

### Hypothesis Details
- Most LLM calls to `list_todos` didn't include a `status` parameter
- The tool filtered by default to `pending` only
- Tasks with `completed` or other statuses were invisible

### Proposed Solution
Change default from `status="pending"` to `status="all"` in both tool files

---

## Analysis Plan

### Steps to Reproduce
1. Have tasks with mixed statuses (some pending, some completed)
2. Call `list_todos` without passing `status`
3. Observe only pending tasks returned

### Expected Outcomes
- After fix, calling without `status` returns ALL tasks for the user

---

## Review / Conclusion

### Results
Fix worked — all tasks are now returned when no status filter is specified.

### Hypothesis Validated?
Yes

### Final Solution
Changed `list_todos(user_id, status="pending")` to `list_todos(user_id, status="all")` in both:
- `backend/mcp_server/tools/list_todos.py`
- `mcp_server/tools/list_todos.py`

The `all` value is handled downstream to skip the status filter entirely.

### Lessons Learned
- Default parameter values in MCP tools directly affect LLM behavior
- When the LLM doesn't pass a parameter, the default is used — so defaults should be the most inclusive option
- Both standalone and backend copies of MCP tools needed the same fix

---

## Related Resources
- `backend/mcp_server/tools/list_todos.py` — MCP tool file
- `mcp_server/tools/list_todos.py` — standalone copy
- `backend/app/routes/tasks.py` — backend endpoint that handles `status="all"` filter
