# Agent Specification: Prompt Logger Agent

> **Agent ID:** PROMPT-LOGGER-001
> **Version:** 1.1
> **Status:** Draft
> **Last Updated:** 2025-12-11

---

## Overview

The Prompt Logger Agent is a **Claude Code development tool** that records user instructions during development sessions. This is NOT a runtime backend agent - it operates within Claude Code IDE integration.

---

## Purpose

- **Audit Trail:** Track instructions given during development
- **Context Reuse:** Reference past prompts in future sessions
- **Documentation:** Auto-generate development history

---

## Agent Configuration

```yaml
agent:
  id: prompt-logger-agent
  name: Prompt Logger Agent
  version: 1.0.0
  description: Automatically logs user prompts to history file

  # Activation
  auto_activate: true
  trigger: on_user_prompt

  # Output configuration
  output:
    file: .claude/prompt-history.md
    format: markdown
    append: true

  # Logging options
  logging:
    include_timestamp: true
    include_type: true
    include_output_reference: true
```

---

## Prompt Record Format

Each logged prompt follows this structure:

```markdown
### PHR-{sequence}: {title}
**Timestamp:** {ISO 8601 timestamp}
**Type:** {Specification|Implementation|Bugfix|Setup|Verification|Research}

{User prompt/instruction text}

**Output:** {Brief description of output or file references}

---
```

---

## Prompt Types

| Type | Description | Example |
|------|-------------|---------|
| `Specification` | Creating or updating specs | "Generate feature spec for..." |
| `Implementation` | Writing code | "Implement the API endpoint..." |
| `Bugfix` | Fixing issues | "Fix the authentication error..." |
| `Setup` | Configuration tasks | "Create uv project and add..." |
| `Verification` | Testing/validation | "Test the API endpoints..." |
| `Research` | Investigation tasks | "Find how the auth system works..." |

---

## Behavior

### On User Prompt
1. Parse incoming user instruction
2. Generate sequence number (PHR-XXX)
3. Determine prompt type from content
4. Extract brief title (first 5-10 words)
5. Record timestamp in ISO 8601 format
6. Append to `.claude/prompt-history.md`

### On Task Completion
1. Update the prompt record with output references
2. List created/modified files
3. Note success/failure status

---

## File Structure

```
.claude/
└── prompt-history.md    # Main prompt history file
```

### History File Format

```markdown
# Prompt History

> Auto-logged user instructions for audit, context reuse, and collaboration.

---

## Session: {YYYY-MM-DD}

### PHR-001: {Title}
**Timestamp:** {timestamp}
**Type:** {type}

{instruction}

**Output:** {output description}

---

### PHR-002: {Title}
...
```

---

## Integration

### With Claude Code
- Runs automatically on each user message
- Non-blocking (doesn't delay responses)
- Silent operation (no user confirmation needed)

**Note:** This is a development-time tool only. It does not integrate with runtime backend agents.

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `true` | Enable/disable logging |
| `file` | `.claude/prompt-history.md` | Output file path |
| `include_code` | `false` | Include code snippets in logs |
| `max_prompt_length` | `500` | Truncate long prompts |
| `session_separator` | `true` | Add date headers for sessions |

---

## Privacy Considerations

- Does NOT log sensitive data (passwords, tokens, secrets)
- Does NOT log file contents unless explicitly requested
- Stored locally in project directory
- Can be gitignored if needed

### .gitignore Entry (Optional)
```
# Uncomment to exclude prompt history from version control
# .claude/prompt-history.md
```

---

## Related Specifications

- `/.claude/prompt-history.md` - Output file

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-10 | Claude | Initial specification |
| 1.1 | 2025-12-11 | Claude | Clarified as dev tool, not runtime agent |
