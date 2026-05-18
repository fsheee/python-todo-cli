Prompt: Fix MCP tools to work with Phase 3 backend + push to GitHub
Date: 2026-05-19
Session work:
1. Updated all 5 MCP tools to call Phase 3 endpoints (/tasks not /api/{uid}/tasks)
2. Changed update_todo from PUT to PATCH
3. Added priority/due_date support to create_todo
4. Force-rebuilt backend Docker image with --no-cache
5. Upgraded Helm release (revision 13)
6. Verified chat "add fee of june RS.5000" creates task successfully
7. Updated DEPLOYMENT_STATUS.md with current state
8. Scrubbed secrets from .env.production and pushed to GitHub
