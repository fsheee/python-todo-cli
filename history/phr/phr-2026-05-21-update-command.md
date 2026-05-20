# PHR: Update Command Failing — Parser, Timestamp, and Scoping Bugs

**Date**: 2026-05-21
**Status**: Completed

## Problem Statement

The `update` command had multiple failure points:
1. The deterministic command parser (`_parse_command`) had no `update` regex — any `update <id> ...` command fell through to the fallback handler
2. The fallback handler (`todo_agent.py`) didn't handle update intent — it only handled `create` and `list`
3. Backend `PATCH /tasks/{id}` crashed with `UnboundLocalError` when `due_date` was not provided in the update payload
4. Backend `PATCH /tasks/{id}` crashed with PostgreSQL `DataError` due to offset-aware `datetime` vs naive database column

### Impact
- **Critical**: Users could not update tasks via chat commands
- Backend returned 500 errors on update requests
- User confusion — "how to edit" was asked

### Context
- Command was: `update <id> set <field> <value>` or `update <id> <value>`
- Error logs showed `UnboundLocalError: local variable 'datetime' referenced before assignment`
- Post-update crash: `DataError: invalid input for TIMESTAMP WITHOUT TIME ZONE`

---

## Hypothesis

### Bug 1: Missing Regex
`_parse_command` didn't match `update` — no word boundary or start-of-string anchor for that keyword in the regex.

### Bug 2: No Update in Fallback
The `todo_agent.py` intent parse only matched `create` and `list` patterns — no `update`/`edit`/`modify` branch.

### Bug 3: Inline Import Scoping
`from datetime import datetime` was written inside a conditional `if due_date:` block. When `due_date` was not provided, `datetime` was never imported, causing `UnboundLocalError`.

### Bug 4: Timezone Mismatch
`datetime.now(timezone.utc)` produces offset-aware datetime (`2025-01-03 12:00:00+00:00`), but the `updated_at` DB column is `TIMESTAMP WITHOUT TIME ZONE`. PostgreSQL rejects this with a `DataError`.

### Proposed Solutions
1. Add update regex to parser
2. Add update intent to fallback handler
3. Move the `datetime` import to module level
4. Use `datetime.utcnow()` (naive UTC) instead of `datetime.now(timezone.utc)`

---

## Analysis Plan

### Steps to Reproduce
1. Send `update e1b5c... set status completed`
2. Observe command parser fails to match — falls through
3. If parser fixed, backend returns `500: UnboundLocalError`
4. If scoping fixed, backend returns `500: DataError`

### Data Collection
- Backend pod logs: `kubectl logs <backend-pod>`
- Specific error: `UnboundLocalError: local variable 'datetime' referenced before assignment at line 178`
- Second error: `DataError: invalid input value for TIMESTAMP`

---

## Review / Conclusion

### Results
All 4 bugs confirmed and fixed.

### Hypothesis Validated?
Yes

### Final Solution
1. **Parser** (`chat.py:56`): Added regex pattern matching `update <id> with|set <field> <value>` and `update <id> with <value>` (value-only, append to title)
2. **Fallback** (`todo_agent.py:125`): Added update intent detection matching `update/edit/modify <id>` patterns
3. **Scoping** (`tasks.py:178`): Moved `from datetime import datetime` to top of file (module-level)
4. **Timezone** (`tasks.py:183`): Changed `datetime.now(timezone.utc)` to `datetime.utcnow()`

Additional improvements:
- When value-only update is used (no field specified), the current title is fetched and the value is appended
- Unrecognized "field names" (e.g. "budget" in "update 3 set budget Rs.5000") are treated as part of the value
- UUID extraction handles both bare UUIDs and `ID:` / backtick-wrapped formats
- Error response from `update_todo` MCP tool now includes backend HTTP status and detail text

### Lessons Learned
- Inline imports inside conditionals are dangerous — always import at module level
- PostgreSQL timezone handling requires matching column type to datetime type
- Always check both the command parser AND the fallback handler when adding a new command
- When deploying to K8s, image tags matter — `:latest` gets pinned by running pods, use unique tags

---

## Related Resources
- `backend/app/routes/chat.py` — `_parse_command` (line 56) and `_execute_command` (line 183)
- `backend/app/routes/tasks.py` — `update_task` PATCH endpoint (line 165)
- `backend/app/agents/todo_agent.py` — fallback handler (line 125)
- `backend/mcp_server/tools/update_todo.py` — MCP tool error handling
- `phase4-k8/docker/backend-phase3.Dockerfile` — Docker build
