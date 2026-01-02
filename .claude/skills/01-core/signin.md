---
name: signin
description: Authenticate user and return tokens. Use for user login.
---

When signing in:

1. **Required**: email, password
2. Verify user exists and password matches
3. Generate access + refresh tokens

Input:
```typescript
{ email, password }
```

Returns user data and tokens on success.
