# PHR: Standalone MCP Server Missing Tool Modules

**Date**: 2026-05-21
**Status**: Completed

## Problem Statement

The standalone MCP server at `backend/mcp_server/` (which connects to `PHASE2_API_URL`) was broken. The `tools/__init__.py` imported modules (`create_todo`, `list_todos`, `update_todo`, `delete_todo`, `search_todos`) that did not exist in that directory. Only `__init__.py` was present — no actual tool `.py` files.

### Impact
- **Critical**: The standalone MCP server (used by the Phase 4 chatbot's MCP tool integration) could not start, making tool-based task operations impossible
- The backend's own `backend/mcp_server/` worked fine, but the standalone copy was non-functional

### Context
- Path: `phase3-chatbot/mcp_server/tools/` — only contained `__init__.py`
- The backend's working copy at `phase3-chatbot/backend/mcp_server/tools/` had all tool files
- Error: `ModuleNotFoundError` when the MCP server tried to import tool modules

---

## Hypothesis

The standalone `mcp_server/tools/` directory was created as a copy/symlink of the backend version but the actual tool modules were never copied over — only the `__init__.py` was created (or the copy omitted the `.py` files).

### Hypothesis Details
- `__init__.py` contained import lines referencing tool modules that didn't exist
- The backend copy had the same import structure but worked because the files were present
- This was likely an incomplete setup or refactoring task

### Proposed Solution
Copy all tool Python files from `backend/mcp_server/tools/` to `mcp_server/tools/`

---

## Analysis Plan

Check the existing files and compare both directories.

### Steps to Reproduce
1. Navigate to `mcp_server/tools/`
2. List files — only `__init__.py` present
3. Try to start the MCP server — `ModuleNotFoundError`

### Data Collection
- `ls -la` on both `mcp_server/tools/` and `backend/mcp_server/tools/`
- Compare `__init__.py` import list with actual files

### Expected Outcomes
- If hypothesis is correct: Files are missing, copying them fixes the import
- If hypothesis is incorrect: Some other issue (e.g., import path, dependencies)

---

## Review / Conclusion

### Results
Hypothesis confirmed — the standalone directory was missing all 5 tool modules.

### Hypothesis Validated?
Yes

### Final Solution
Copied `create_todo.py`, `list_todos.py`, `update_todo.py`, `delete_todo.py`, `search_todos.py` from `backend/mcp_server/tools/` to `mcp_server/tools/`

### Lessons Learned
- When setting up parallel MCP server instances, ensure all tool modules are present in both
- Add a startup check that verifies all expected modules can be imported
- Consider a shared tool module location to prevent drift

---

## Related Resources
- `phase3-chatbot/mcp_server/tools/__init__.py` — had imports for missing modules
- `phase3-chatbot/backend/mcp_server/tools/` — source of the working tool files
