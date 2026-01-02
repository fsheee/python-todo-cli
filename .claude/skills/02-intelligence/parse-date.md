---
name: parse-date
description: Parse natural language date expressions. Use for extracting due dates.
---

When parsing dates:

Convert natural language to ISO 8601 format:

- "today" → current date
- "tomorrow" → +1 day
- "next Friday" → next Friday's date
- "in 3 days" → +3 days
- "next week" → +7 days
- "end of month" → last day of current month

Returns ISO 8601 date string.
