# ADR: Adding update to the Deterministic Command Parser

**Date**: 2026-05-21
**Status**: Accepted

## Context

The chatbot uses a two-tier command handling system:
1. **Deterministic command parser** (_parse_command in chat.py): regex-based, handles structured commands instantly without LLM round-trip
2. **LLM fallback handler** (	odo_agent.py): for ambiguous/natural language, slower but more flexible

The system supported create/list/delete/search in the deterministic parser but not update. All update requests fell through to the fallback handler, which also didn't handle update intent.

## Decision

Add update to the deterministic command parser with the following patterns:

| Pattern | Example | Behavior |
|---------|---------|----------|
| update <id> with <value> | update abc123 with buy milk | Appends value to existing title |
| update <id> set <field> <value> | update abc123 set status completed | Updates specific field |
| update <id> set <field> to <value> | update abc123 set status to completed | Same as above with optional "to" |
| update <id> | update abc123 | Falls through to LLM fallback |

### Key Design Choices

1. **Value-only appends to title** — when no field keyword is recognized, the entire remainder is appended to the current title (separated by space). This handles "Rs.5000" style additions without needing a dedicated mount field.

2. **Unknown "fields" are treated as part of the value** — e.g., update abc123 set budget Rs.5000 — since "budget" is not a recognized field, the entire "budget Rs.5000" is appended to the title.

3. **UUID extraction handles multiple formats** — bare UUIDs, ID: prefix, and backtick-wrapped formats are all supported.

4. **No new DB schema** — updates use existing 	itle/description/status/priority/due_date fields. No mount column was added.

## Consequences

### Positive
- Update commands are now fast (no LLM round-trip)
- Users can use natural value-only updates like "update task 123 with Rs.5000"
- Consistent with existing parser patterns
- No schema migration needed

### Negative
- The "unknown field = part of value" heuristic could cause surprising behavior if a real field name is misspelled (e.g., update abc123 set statis done)
- Appending to title is a simple heuristic — no natural language parsing of "Rs.5000" vs "add Rs.5000 as budget"
- Title can grow long if users repeatedly append

### Neutral
- Users who want specific field updates must use the exact field keyword (status, 	itle, description, priority, due_date)
- LLM fallback still available for complex/ambiguous update requests
