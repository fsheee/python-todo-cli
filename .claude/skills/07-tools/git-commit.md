---
name: git-commit
description: Create git commits with proper format. Use when saving changes.
---

When committing:

1. **Stage changes**: `git add <files>` or `git add .`
2. **Write commit message**:
   - First line: Summary (50 chars max)
   - Body: Detailed explanation (72 chars per line)
3. **Format**: Use conventional commits
   ```
   feat: add new user signup
   fix: resolve login bug
   docs: update README
   refactor: simplify auth logic
   ```

4. **Example**:
   ```
   git add .
   git commit -m "feat: add task search functionality

   - Search tasks by title and description
   - Add pagination to results
   - Update API documentation"
   ```

5. **Push after commit**: `git push`
