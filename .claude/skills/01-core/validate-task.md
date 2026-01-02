---
name: validate-task
description: Validate task input data. Use before create/update operations.
---

When validating task input:

1. **Title**: 1-255 chars, required for create
2. **Description**: 0-2000 chars, optional
3. **Priority**: low/medium/high, defaults to medium
4. **Due date**: ISO 8601 format, optional

Returns validation errors with field and message if invalid.
